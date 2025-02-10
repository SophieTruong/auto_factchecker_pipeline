from sklearn.metrics import f1_score, precision_score, recall_score, accuracy_score
from typing import List
def calculate_metrics(y_true: List[int], y_pred: List[int]):
    return {
        "f1_score": f1_score(y_true, y_pred),
        "f1_micro": f1_score(y_true, y_pred, average="micro"),
        "f1_macro": f1_score(y_true, y_pred, average="macro"),
        "f1_weighted": f1_score(y_true, y_pred, average="weighted"),
        "precision": precision_score(y_true, y_pred),
        "recall": recall_score(y_true, y_pred),
        "accuracy": accuracy_score(y_true, y_pred)
    }