"""
There are 2 types of queries:
1. Write metric log to metric table
2. Read metric log from metric table
"""
from sqlalchemy.orm import Session
from database.model import Metric

from datetime import datetime

def write_metric(db: Session, metric: dict):
    metric = Metric(
        model_id=metric["model_id"],
        start_date=metric["start_date"],
        end_date=metric["end_date"],
        f1_score=metric["f1_score"],
        f1_micro=metric["f1_micro"],
        f1_macro=metric["f1_macro"],
        f1_weighted=metric["f1_weighted"],
        precision=metric["precision"],
        recall=metric["recall"],
        accuracy=metric["accuracy"]
    )
    db.add(metric)
    db.commit()
    db.refresh(metric)
    return metric

def read_metric(db: Session, start_date: datetime, end_date: datetime):
    return db.query(Metric).filter(Metric.start_date >= start_date, Metric.end_date <= end_date).all()

def get_last_log(db: Session):
    return db.query(Metric).order_by(Metric.end_date.desc()).first()