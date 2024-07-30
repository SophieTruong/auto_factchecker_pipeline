import os
from dotenv import load_dotenv
load_dotenv()

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename='xmlroberta-tunning.log', encoding='utf-8', level=logging.DEBUG)

import torch
torch.cuda.empty_cache()

import numpy as np
import evaluate

from datasets import Dataset, load_from_disk
from transformers import (
    XLMRobertaTokenizer,
    XLMRobertaForSequenceClassification,
    TrainingArguments,
    Trainer,
    AutoConfig,
    DataCollatorWithPadding
)

# Model tracking
import mlflow

# Model parameter tuning
import optuna

def load_datasets(train_path: str, test_path: str, validation_path: str | None = None):
    """
    Return train, validation, and test dataset found from the paths provided in parameters
    """
    train_dataset = load_from_disk(train_path)
    test_dataset = load_from_disk(test_path)
    if validation_path:
        val_dataset = load_from_disk(validation_path)
        return train_dataset, val_dataset, test_dataset
    return train_dataset, test_dataset

# # This function tokenizes the input text using the RoBERTa tokenizer. 
# # It applies padding and truncation to ensure that all sequences have the same length (256 tokens).
# def tokenize(batch):
#     return tokenizer(batch["text"], padding=True, truncation=True, max_length=256)

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return metric.compute(predictions=predictions, references=labels)

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
    with mlflow.start_run(nested=True):
        # Define hyperparameters
        params = {
            "num_train_epochs": 2, #trial.suggest_int("num_train_epochs", 2, 5, log=True),
            "per_device_train_batch_size": trial.suggest_categorical("per_device_train_batch_size", [16,32]),
            "per_device_eval_batch_size": 8,#trial.suggest_int("per_device_eval_batch_size", 8, 16, step=8),
            "learning_rate": trial.suggest_float("learning_rate", 5e-6, 1e-5, log=True),
        }
        
        # TrainingArguments
        training_args = TrainingArguments(
            output_dir=f"{output_dir}",
            num_train_epochs=params["num_train_epochs"], # TUNE
            per_device_train_batch_size=params["per_device_train_batch_size"], # TUNE
            per_device_eval_batch_size=params["per_device_eval_batch_size"], # TUNE
            evaluation_strategy="epoch",
            logging_dir=f"{output_dir}/logs",
            logging_strategy="steps",
            logging_steps=10, 
            learning_rate=params["learning_rate"], # TUNE
            weight_decay=0.01,
            warmup_steps=500,
            save_strategy="epoch",
            load_best_model_at_end=True,
            save_total_limit=2,
            report_to="mlflow",
        )

        # Trainer
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_token,      
            eval_dataset=val_token,         
            tokenizer=tokenizer,            
            compute_metrics=compute_metrics,
            data_collator=data_collator,    
        )
        
        # Train
        trainer.train()
        
        # Evaluate model performance on test set
        predicts = trainer.predict(test_token)
        predictions = np.argmax(predicts.predictions, axis=-1)
        labels = predicts.label_ids

        accuracy = evaluate.load("accuracy")
        recall = evaluate.load("recall")
        precision = evaluate.load("precision")
        f1 = evaluate.load("f1")
        obj_metric = evaluate.combine(["accuracy","f1","recall","precision"])

        test_results = obj_metric.compute(predictions=predictions, references=labels)

        # Log to MLflow
        mlflow.log_params(params)
        
        mlflow.log_metric("test_accuracy", test_results["accuracy"])
        mlflow.log_metric("test_recall", test_results["recall"])
        mlflow.log_metric("test_precision", test_results["precision"])
        mlflow.log_metric("test_f1", test_results["f1"])
        
    return test_results["f1"] # Return best F1 score for test set

if __name__ == "__main__":
    
    # mlflow + databrick connection
    mlflow.set_tracking_uri("databricks")
    
    # override Optuna's default logging to ERROR only
    optuna.logging.set_verbosity(optuna.logging.ERROR)


    ## TODO: Use parser to load params################################################
    model_id = "FacebookAI/xlm-roberta-base"

    train_path = "./data/tokenized_dataset/train"
    test_path = "./data/tokenized_dataset/test"
    validation_path = "./data/tokenized_dataset/val"
    test = False
    ##################################################################################
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    print(f"Device is: {device}")
    
    # Preprocessing
    tokenizer = XLMRobertaTokenizer.from_pretrained(model_id)
    
    train_token, val_token, test_token = load_datasets(train_path, test_path, validation_path)

    # We will need this to directly output the class names when using the pipeline without mapping the labels later.
    # Extract the number of classes and their names
    num_labels = 2
    class_names = [0,1]
    print(f"number of labels: {num_labels}")
    print(f"the labels: {class_names}")

    # Create an id2label mapping
    id2label = {0: "non_check_worthy", 1: "check_worthy"}

    # Update the model's configuration with the id2label mapping
    config = AutoConfig.from_pretrained(model_id)
    config.update({"id2label": id2label})

    # Set up tracking
    experiment_name = f"/Users/{os.getenv('MLFLOW_TRACKING_USERNAME')}/xml-roberta-claim-detection-dime"
    experiment_id = get_or_create_experiment(experiment_name)

    mlflow.set_experiment(
        experiment_id = experiment_id
    )
    
    # Metrics
    accuracy = evaluate.load("accuracy")
    recall = evaluate.load("recall")
    precision = evaluate.load("precision")
    f1 = evaluate.load("f1")
    metric = evaluate.combine(["accuracy","f1","recall","precision"])
    
    # Data collator for tokenizer
    data_collator = DataCollatorWithPadding(tokenizer)

    # Model
    model = XLMRobertaForSequenceClassification.from_pretrained(model_id, config=config)
    model.to(device)

    output_dir = "./xml-roberta-test" if test else "./xml-roberta-model"
            
    run_name = "hyperparams-tuning-clef-21-24"

    # Initiate the parent run and call the hyperparameter tuning child run logic
    with mlflow.start_run(experiment_id=experiment_id, run_name=run_name, nested=True):
        # Initialize the Optuna study
        study = optuna.create_study(direction="maximize")

        # Execute the hyperparameter optimization trials.
        # Note the addition of the `champion_callback` inclusion to control our logging
        study.optimize(objective, n_trials=10, callbacks=[champion_callback])

        mlflow.log_params(study.best_params)
        mlflow.log_metric("best_f1", study.best_value)

        # Log tags
        mlflow.set_tags(
            tags={
                "project": "DIME Claim Detection model",
                "optimizer_engine": "optuna",
                "model_family": "xml-roberta",
                "feature_set_version": 1,
            }
        )

        # Fine-tune the model
        # TrainingArguments
        training_args = TrainingArguments(
            output_dir=f"{output_dir}",
            num_train_epochs=2, #study.best_params["num_train_epochs"],
            per_device_train_batch_size=study.best_params["per_device_train_batch_size"],
            per_device_eval_batch_size=8, #study.best_params["per_device_eval_batch_size"],
            evaluation_strategy="epoch",
            logging_dir=f"{output_dir}/logs",
            logging_strategy="steps",
            logging_steps=10, 
            learning_rate=study.best_params["learning_rate"],
            weight_decay=0.01,
            warmup_steps=500,
            save_strategy="epoch",
            load_best_model_at_end=True,
            save_total_limit=2,
            report_to="mlflow",
        )

        # Trainer
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_token,
            eval_dataset=val_token,
            tokenizer=tokenizer,
            compute_metrics=compute_metrics,
            data_collator=data_collator,
        )

        trainer.train()
        trainer.save_model(output_dir)

        # Evaluate the model
        trainer.evaluate()
        
        artifact_path = "model"

        model_info = mlflow.transformers.log_model(
            transformers_model={"model": trainer.model, "tokenizer": tokenizer},
            artifact_path=artifact_path,
            task="text-classification",
            metadata={"model_data_version": 1},
        )
        
        # Get the logged model uri so that we can load it from the artifact store
        model_uri = mlflow.get_artifact_uri(artifact_path)
        print(model_uri)
        logger.info('MLFLOW model_uri: %s', model_uri)
        logger.info('SUCCEED')


