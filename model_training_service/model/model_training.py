
import os
import sys
import json
import uuid
sys.path.append(os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath("__file__"))))
               )

sys.path.append(os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath("__file__"))),
                'model_training_service')
               )
sys.path.append(os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath("__file__"))),
                'model_training_service',
                'data')
               )

print(sys.path)

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

from data.data_processing import get_text_label, get_data_splits, shape_data

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from setfit import SetFitModel, Trainer, TrainingArguments, sample_dataset
from sentence_transformers import InputExample, SentenceTransformer, losses

from sklearn.metrics import f1_score, balanced_accuracy_score, accuracy_score, confusion_matrix, multilabel_confusion_matrix

import torch

import evaluate

# Model tracking
import wandb
import mlflow
from mlflow.models import infer_signature
from mlflow.pyfunc import PythonModel


# Model parameter tuning
import optuna

class SetFitCustomModel(PythonModel):
    def load_context(self, context):
        self.model = SetFitModel.from_pretrained(context.artifacts['snapshot'])

    def predict(self, context, model_input):
        predicts = self.model.predict(model_input)
        return predicts

def get_or_create_experiment(experiment_name):
    """
    Retrieve the ID of an existing MLflow experiment or create a new one if it doesn't exist.

    This function checks if an experiment with the given name exists within MLflow.
    If it does, the function returns its ID. If not, it creates a new experiment
    with the provided name and returns its ID.

    Parameters:
    - experiment_name (str): Name of the MLflow experiment.

    Returns:
    - str: ID of the existing or newly created MLflow experiment.
    """

    if experiment := mlflow.get_experiment_by_name(experiment_name):
        return experiment.experiment_id
    else:
        return mlflow.create_experiment(experiment_name)

# define a logging callback that will report on only new challenger parameter configurations if a
# trial has usurped the state of 'best conditions'
def champion_callback(study, frozen_trial):
    """
    Logging callback that will report when a new trial iteration improves upon existing
    best trial values.

    Note: This callback is not intended for use in distributed computing systems such as Spark
    or Ray due to the micro-batch iterative implementation for distributing trials to a cluster's
    workers or agents.
    The race conditions with file system state management for distributed trials will render
    inconsistent values with this callback.
    """

    winner = study.user_attrs.get("winner", None)

    if study.best_value and winner != study.best_value:
        study.set_user_attr("winner", study.best_value)
        if winner:
            improvement_percent = (abs(winner - study.best_value) / study.best_value) * 100
            print(
                f"Trial {frozen_trial.number} achieved value: {frozen_trial.value} with "
                f"{improvement_percent: .4f}% improvement"
            )
        else:
            print(f"Initial trial {frozen_trial.number} achieved value: {frozen_trial.value}")


def objective(trial):
    # Load data
    data_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath("__file__"))),
                'model_training_service', 
                os.environ.get("DATA_PATH")
    )
    
    texts, labels = get_text_label(data_path)
    
    # Create data splits
    train_df, test_df1, dev_df, test_scores= get_data_splits(1, texts, labels)
            
    train_ds, test_ds, dev_ds, test_df= shape_data(train_df, test_df1, dev_df, False)

    # Set model
    model, pretrained_model_name = set_model()

    with mlflow.start_run(nested=True):
        
        run_id = mlflow.active_run().info.run_id
        uuid_str = str(uuid.uuid4())
        
        print(f"Run ID: {run_id}, UUID: {uuid_str}")
        
        # Define hyperparameters
        params = {
            "num_epochs": trial.suggest_int("num_epochs", 2, 4, log=True),
            "batch_size": trial.suggest_categorical("batch_size", [16,32]),
            "num_iterations": trial.suggest_int("num_iterations", 6, 8, log=True),
        }
        
        print(f"Hyperparameters during trial: {params}") 
        
        # TrainingArguments
        training_args = TrainingArguments(
            num_epochs=params["num_epochs"],
            eval_strategy="epoch",
            save_strategy="epoch",
            logging_strategy="epoch",
            num_iterations=params["num_iterations"],
            loss=losses.CosineSimilarityLoss,
            report_to="mlflow",
        )
        
        training_args.eval_strategy = training_args.eval_strategy

        # Trainer
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_ds,      
            eval_dataset=dev_ds,         
            metric= f1_score_weighted
        )
        
        # Train
        trainer.train()
        
        # Evaluate model
        metric = trainer.evaluate()
        print(f"Hyperparameters: {params}, f1_score_weighted: {metric['metric']}")

        # Log to MLflow
        
        mlflow.log_params({f"{uuid_str}_{k}":v for k,v in params.items()})
        
        mlflow.log_metric("f1_score_weighted", metric['metric'])
        
    return metric['metric']


def set_model(multi_label=False):
    # Load a SetFit model from Hub 
    pretrained_model_name = 'FacebookAI/xlm-roberta-base' #'TurkuNLP/bert-base-finnish-cased-v1'
    if multi_label:
        model = SetFitModel.from_pretrained(pretrained_model_name, multi_target_strategy="multi-output")
    else:
        model = SetFitModel.from_pretrained(pretrained_model_name)
    return model, pretrained_model_name

def config_wandb(multi_label, pretrained_model_name, config=None):
    if config is None:
        config = {'learning_rate': 3.0191843531454982e-05, 'num_epochs': 4, 'batch_size': 16, 'seed': 34, 'num_iterations': 6}

    wandb.init(
        project="Claim-detection",
        notes="initial",
        tags=["Henna", "binary", "single label" if multi_label else 'binary', 'first_test', 'DIME_data_HennaPipsaMinttu', 'ei-tark_henkkoht_muu==0', pretrained_model_name],
        config=config,
    )
    return wandb, config 
    
def f1_score_weighted(y_true, y_pred):
    return f1_score(y_true.numpy(), np.array(y_pred), average='weighted')

def train_model(model, train_ds, dev_ds, config):
    print(f"Training model with config: {config}")
    
    args = TrainingArguments(
        batch_size=config["batch_size"],
        num_epochs=config["num_epochs"],
        eval_strategy="epoch", #"epoch",
        save_strategy="epoch", #"epoch",
        load_best_model_at_end=False,
        num_iterations=config["num_iterations"],
        loss=losses.CosineSimilarityLoss,
        report_to="mlflow",
    )
    args.eval_strategy = args.evaluation_strategy
    
    trainer = Trainer(
        model=model,
        train_dataset=train_ds,
        args=args,
        eval_dataset=dev_ds,
        metric= f1_score_weighted
    )

    # Train and evaluate
    trainer.train()
    metric = trainer.evaluate()
    print(metric)
    return model, metric, trainer

def get_predictions(model, test_df, multi_label):    
    # model = new_model
    # Run inference
    preds = model.predict(test_df['text'], as_numpy=True)
    probs = model.predict_proba(test_df['text'], as_numpy=True)
    probsmax = np.max(probs, axis=1)

    if not multi_label:
        # preds_labels = [classes[i] for i in preds]
        y_true = test_df['label']
        y_pred = preds
    else:
        y_true = test_df.drop(columns=['text']).values
        y_pred = preds
    return preds, probs, y_true, y_pred #probsmax


def print_confusion_matrix(confusion_matrix_data, axes, class_label, class_names, fontsize=14):

    df_cm = pd.DataFrame(
        confusion_matrix_data, index=class_names, columns=class_names,
    )

    try:
        heatmap = sns.heatmap(df_cm, annot=True, fmt="d", cbar=False, ax=axes)
    except ValueError:
        raise ValueError("Confusion matrix values must be integers.")
    heatmap.yaxis.set_ticklabels(heatmap.yaxis.get_ticklabels(), rotation=0, ha='right', fontsize=fontsize)
    heatmap.xaxis.set_ticklabels(heatmap.xaxis.get_ticklabels(), rotation=45, ha='right', fontsize=fontsize)
    axes.set_ylabel('True label')
    axes.set_xlabel('Predicted label')
    axes.set_title("Confusion Matrix for the class - " + class_label)

def get_confusion_matrix(multi_label, wandb, y_true, y_pred, classes):
    if not multi_label:
        wandb.log({"confusion matrix" : wandb.plot.confusion_matrix(probs=None,
                                y_true=y_true, preds=y_pred,
                                class_names=classes)})

        cm = confusion_matrix(y_true, y_pred)
        df_cm = pd.DataFrame(cm, index = classes, columns = classes)
        plt.figure(figsize = (10,7))
        sns.heatmap(df_cm, annot=True)
    else:
        cm = multilabel_confusion_matrix(y_true, y_pred)

        fig, ax = plt.subplots(5, 3, figsize=(12, 12))

        for axes, cfs_matrix, label in zip(ax.flatten(), cm, classes):
            print_confusion_matrix(cfs_matrix, axes, label, ["N", "Y"])

        fig.tight_layout()
        plt.show()   
        wandb.log({"confusion matrix 2": wandb.Image(plt)})
        
def get_classification_report(y_true, y_pred):
    classes0 = ['True', 'False']
    from sklearn.metrics import classification_report
    print(classification_report(y_true, y_pred, target_names=classes0, zero_division=0))

def get_evaluation_metrics(y_true, y_pred, probs, preds, wandb):
    micro_f1_score = f1_score(y_true, y_pred, average='micro')
    wandb.log({"f1-score micro": micro_f1_score})
    print('f1-score micro', f1_score(y_true, y_pred, average='micro'))

    macro_f1_score = f1_score(y_true, y_pred, average='macro')
    wandb.log({"f1-score macro": macro_f1_score})
    print('f1-score macro', macro_f1_score)

    weighted_f1_score = f1_score(y_true, y_pred, average='weighted')
    wandb.log({"f1-score weighted": weighted_f1_score})
    print('f1-score weighted', weighted_f1_score)

    balanced_accuracy = balanced_accuracy_score(y_true, y_pred)
    wandb.log({"balanced accuracy": balanced_accuracy})
    print('balanced accuracy', balanced_accuracy)
    
    accuracy = accuracy_score(y_true, y_pred)
    wandb.log({"accuracy": accuracy})
    print('accuracy ', accuracy)
    
    return balanced_accuracy, accuracy, macro_f1_score, micro_f1_score, weighted_f1_score
    
def write_metrics_to_file(state_r, balanced_accuracy, accuracy, macro_f1_score, micro_f1_score, weighted_f1_score,pretrained_model_name):
    lines= [' ,', ' ,',pretrained_model_name, ' ,',str(state_r),' ,', 'DIME_data_HennaMinttuPipsa_all_labels',' ,', 'balanced_accuracy:',' ,', str(balanced_accuracy),' ,', 'accuracy:',' ,', str(accuracy),' ,',
       'macro-f1:',' ,', str(macro_f1_score),' ,', 'micro_f1_score:',' ,', str(micro_f1_score),' ,', 'weighted f1:', ' ,',str(weighted_f1_score),' ,', '\n']

    with open('setfit_claim_detection_DIME_data_HennaMinttuPipsa_all_labels_henkkoht-eitarkist-muu==0.txt', 'a') as f:
        f.writelines(lines)
        
def main():
    # setting device on GPU if available, else CPU
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print('Using device:', device)
    print()
    
    #Additional Info when using cuda
    if device.type == 'cuda':
        print(torch.cuda.get_device_name(0))

    # Load data
    data_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath("__file__"))),
                'model_training_service', 
                os.environ.get("DATA_PATH")
    )
    multi_label = False

    # Inspect the data reading, spliting code
    random_states=[7,8,9,10]#[1,2,3,4,5,6,]

    texts, labels = get_text_label(data_path)
    
    # override Optuna's default logging to ERROR only
    optuna.logging.set_verbosity(optuna.logging.ERROR)
    
    # Set up MLFlow tracking
    experiment_name = f"/Users/{os.getenv('MLFLOW_TRACKING_USERNAME')}/claim-detection-setfit-Facebook-XML"
    experiment_id = get_or_create_experiment(experiment_name)
    print(f"Experiment ID: {experiment_id}")
    print(f"Experiment Name: {experiment_name}")
    
    mlflow.set_experiment(
        experiment_id = experiment_id
    )
    run_name = "setfit-Facebook-XML-Henna-training"
    with mlflow.start_run(experiment_id=experiment_id, run_name=run_name, nested=True):
        # Initialize the Optuna study
        study = optuna.create_study(direction="maximize")

        # Execute the hyperparameter optimization trials.
        # Note the addition of the `champion_callback` inclusion to control our logging
        study.optimize(objective, n_trials=10, callbacks=[champion_callback])
        
        optuna_best_params = study.best_params
        optuna_best_value = study.best_value
        print(f"Optuna best params: {optuna_best_params}, Optuna best value: {optuna_best_value}")
        
        # Log the best hyperparameters
        mlflow.log_params(optuna_best_params)
        mlflow.log_metric("best_f1", optuna_best_value)
        
        # Log tags
        mlflow.set_tags(
            tags={
                "project": "DIME Claim Detection model",
                "optimizer_engine": "optuna",
                "model_family": "setfit-Facebook-XML",
                "feature_set_version": 1,
                "dataset": "DIME_data_HennaPipsaMinttu",
                "label": "ei-tark_henkkoht_muu==0",
            }
        )
        
        for state_x in random_states:
            with mlflow.start_run(nested=True):
                train_df, test_df1, dev_df, test_scores= get_data_splits(state_x, texts, labels)
            
                train_ds, test_ds, dev_ds, test_df= shape_data(train_df, test_df1, dev_df, multi_label)
            
                model, pretrained_model_name = set_model()
            
                wandb, config= config_wandb(multi_label, pretrained_model_name, optuna_best_params) 
            
                model, metric, trainer= train_model(model, train_ds, dev_ds, config) 
                
                preds, probs, y_true, y_pred= get_predictions(model, test_df, multi_label)
            
                get_classification_report(y_true, y_pred)
            
                balanced_accuracy, accuracy, macro_f1_score, micro_f1_score, weighted_f1_score= get_evaluation_metrics(y_true, y_pred,probs, preds, wandb)
            
                write_metrics_to_file(state_x, balanced_accuracy, accuracy, macro_f1_score, micro_f1_score, weighted_f1_score,pretrained_model_name)
                            
                # First, save the finetuned model locally
                model.save_pretrained('snapshot')

                # Log the hyperparameters
                config["train_test_split_random_state"] = state_x
                mlflow.log_params({
                    "train_test_split_random_state":state_x,
                    "device": torch.cuda.get_device_name(0)
                })

                # Log the loss metric
                mlflow.log_metric("f1-score micro", micro_f1_score)
                mlflow.log_metric("f1-score macro", macro_f1_score)
                mlflow.log_metric("f1-score weighted", weighted_f1_score)
                mlflow.log_metric("balanced accuracy", balanced_accuracy)
                mlflow.log_metric("accuracy", accuracy)
                
                # Log the model
                artifact_path = "setfit_model"
                model_info = mlflow.pyfunc.log_model(
                    artifact_path=artifact_path,
                    artifacts={'snapshot': 'snapshot'},
                    python_model=SetFitCustomModel(),
                    conda_env='conda-env.yml',
                    registered_model_name="claim-detection-setfit-TurkuNLP",
                )
                # Get the logged model uri so that we can load it from the artifact store
                model_uri = mlflow.get_artifact_uri(artifact_path)
                print(model_uri)
                print('MLFLOW model_uri: %s', model_uri)
                print('SUCCEED')
                with open('mlflow_model_uri.json', 'w') as f:
                    json.dump({
                        "model_uri": model_uri, 
                        "experiment_id": experiment_id, 
                        "artifact_path": artifact_path,
                        "pretrained_model_name": pretrained_model_name,
                        "config": config
                    }, f)


if __name__ == "__main__":
    main()
        
