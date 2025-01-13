from datetime import datetime
from typing import List

from sqlalchemy import select, insert, update, delete
from sqlalchemy.sql import func

from .models import Claim, SourceDocument, ClaimModelInference, ClaimDetectionModel, ClaimAnnotation
from .utils import cast_language_literal, sanitize_string

## Source Document Queries
def insert_source_document_query(source_document_data: dict):
    """
    Create a query for inserting source documents
    """
    return insert(SourceDocument).values(source_document_data).returning(SourceDocument)

def get_source_document_by_id_query(source_document_id: int):
    """
    Create a query for a source document by its ID
    """
    return select(SourceDocument).where(SourceDocument.id == source_document_id)

def get_source_document_by_text_query(text: str):
    """
    Create a query for a source document by its text
    """
    sanitized_text = sanitize_string(text)
    
    return select(SourceDocument).where(
        func.to_tsvector(
            cast_language_literal("finnish"),
            SourceDocument.text
        ).bool_op("@@")(
            func.websearch_to_tsquery(
                cast_language_literal("finnish"),
                sanitized_text
            )
        )
    )

def update_source_document_query(source_document_id: int, source_document_data: dict):
    """
    Create a query for updating a source document
    """
    return update(SourceDocument).where(SourceDocument.id == source_document_id).values(source_document_data).returning(SourceDocument)

def delete_source_document_query(source_document_id: int):
    """
    Create a query for deleting a source document
    """
    return delete(SourceDocument).where(SourceDocument.id == source_document_id).returning(SourceDocument)

## Claim Queries
def get_claim_by_id_query(claim_id: int):
    """
    Create a query for a claim by its ID
    """
    return select(Claim).where(Claim.id == claim_id)

def get_claims_by_time_range_query(start_date: datetime, end_date: datetime):
    """
    Create a query for claims by their creation date range
    """
    return select(Claim).where(Claim.created_at >= start_date, Claim.created_at <= end_date)

def get_claim_by_text_query(text: str):
    """
    Create a text search query for claims
    """
    sanitized_text = sanitize_string(text)
    
    return select(Claim).where(
        func.to_tsvector(
            cast_language_literal("finnish"),
            Claim.text
        ).bool_op("@@")(
            func.websearch_to_tsquery(
                cast_language_literal("finnish"),
                sanitized_text
            )
        )
    )

def insert_claims_query(claims_data: List[dict]):
    """
    Create a query for inserting claims
    """
    return insert(Claim).values(claims_data).returning(Claim)

def update_claim_query(claim_id: int, claim_data: dict):
    """
    Create a query for updating a claim
    """
    return update(Claim).where(Claim.id == claim_id).values(claim_data).returning(Claim)

def delete_claim_query(claim_id: int):
    """
    Create a query for deleting a claim
    """
    return delete(Claim).where(Claim.id == claim_id).returning(Claim)

## Claim Model Inference Queries
def insert_claim_model_inference_query(claim_model_inference_data: List[dict]):
    """
    Create a query for inserting claim model inferences
    """
    return insert(ClaimModelInference).values(claim_model_inference_data).returning(ClaimModelInference)

def get_claim_model_inference_by_id_query(claim_model_inference_id: int):
    """
    Create a query for a claim model inference by its ID
    """
    return select(ClaimModelInference).where(ClaimModelInference.id == claim_model_inference_id)

def get_claim_model_inference_by_claim_id_query(claim_id: int):
    """
    Create a query for a claim model inference by its claim ID
    """
    return select(ClaimModelInference).where(ClaimModelInference.claim_id == claim_id)

def update_claim_model_inference_query(claim_model_inference_id: int, claim_model_inference_data: dict):
    """
    Create a query for updating a claim model inference
    """
    return update(ClaimModelInference).where(ClaimModelInference.id == claim_model_inference_id).values(claim_model_inference_data).returning(ClaimModelInference)

def update_claim_model_inference_by_claim_id_query(claim_id: int, claim_model_inference_data: dict):
    """
    Create a query for updating a claim model inference by its claim ID
    """
    return update(ClaimModelInference).where(ClaimModelInference.claim_id == claim_id).values(claim_model_inference_data).returning(ClaimModelInference)

def delete_claim_model_inference_query(claim_model_inference_id: int):
    """
    Create a query for deleting a claim model inference
    """
    return delete(ClaimModelInference).where(ClaimModelInference.id == claim_model_inference_id).returning(ClaimModelInference)

## Claim Detection Model Queries
def insert_claim_detection_model_query(claim_detection_model_data: dict):
    """
    Create a query for inserting claim detection models
    """
    return insert(ClaimDetectionModel).values(claim_detection_model_data).returning(ClaimDetectionModel)

def get_claim_detection_model_by_id_query(claim_detection_model_id: int):
    """
    Create a query for a claim detection model by its ID
    """
    return select(ClaimDetectionModel).where(ClaimDetectionModel.id == claim_detection_model_id)

def update_claim_detection_model_query(claim_detection_model_id: int, claim_detection_model_data: dict):
    """
    Create a query for updating a claim detection model
    """
    return update(ClaimDetectionModel).where(ClaimDetectionModel.id == claim_detection_model_id).values(claim_detection_model_data).returning(ClaimDetectionModel)

def delete_claim_detection_model_query(claim_detection_model_id: int):
    """
    Create a query for deleting a claim detection model
    """
    return delete(ClaimDetectionModel).where(ClaimDetectionModel.id == claim_detection_model_id).returning(ClaimDetectionModel)

## Claim Annotation Queries
def insert_claim_annotation_query(claim_annotation_data: List[dict]):
    """
    Create a query for inserting claim annotations
    """
    return insert(ClaimAnnotation).values(claim_annotation_data).returning(ClaimAnnotation)

def get_claim_annotation_by_id_query(claim_annotation_id: int):
    """
    Create a query for a claim annotation by its ID
    """
    return select(ClaimAnnotation).where(ClaimAnnotation.id == claim_annotation_id)

def get_claim_annotation_by_source_document_id_query(source_document_id: int):
    """
    Create a query for a claim annotation by its source document ID
    """
    return select(ClaimAnnotation).where(ClaimAnnotation.source_document_id == source_document_id)

def update_claim_annotation_query(claim_annotation_id: int, claim_annotation_data: dict):
    """
    Create a query for updating a claim annotation
    """
    return update(ClaimAnnotation).where(ClaimAnnotation.id == claim_annotation_id).values(claim_annotation_data).returning(ClaimAnnotation)

def delete_claim_annotation_query(claim_annotation_id: int):
    """
    Create a query for deleting a claim annotation
    """
    return delete(ClaimAnnotation).where(ClaimAnnotation.id == claim_annotation_id).returning(ClaimAnnotation)