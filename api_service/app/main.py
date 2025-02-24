from typing import List, Optional, Annotated

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from fastapi.security import APIKeyHeader

from sqlalchemy.orm import Session

# Import pydantic models
from models.claim import Claim
from models.claim_detection_response import BatchClaimResponse
from models.source_document import SourceDocumentCreate
from models.claim_annotation_input import BatchClaimAnnotationInput
from models.claim_annotation import ClaimAnnotation
from models.semantic_search_input import SemanticSearchInput
from models.semantic_search_response import BatchSemanticSearchResponse
from models.claim_model_monitoring import ClaimModelMonitoring

# Import database models
from database.postgres import engine, Base, SessionLocal, get_db
from database.crud import get_all_api_keys

# Import services
from services.claim_detection import ClaimDetectionService
from services.claim_annotation import ClaimAnnotationService
from services.semantic_search import SemanticSearchService
from services.claim_model_monitoring_data import ClaimModelMonitoringService

# Import utils
from utils.app_logging import logger
from utils.password_hashing import verify_password

from datetime import datetime

import dotenv
import os
dotenv.load_dotenv(dotenv.find_dotenv())

# Setup logging
logger.info('API is starting up')

# Setup inference model uri
INFERENCE_MODEL_URI = "http://model_inference:8090/predict" if not os.getenv('INFERENCE_MODEL_URI') else os.getenv('INFERENCE_MODEL_URI')
logger.info(f"*** INFERENCE_MODEL_URI: {INFERENCE_MODEL_URI}")

SEMANTIC_SEARCH_URI = "http://evidence_retrieval:8091/semantic_search"
logger.info(f"*** SEMANTIC_SEARCH_URI: {SEMANTIC_SEARCH_URI}")

# Set up FastAPI
app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up postgresql db dependancies
Base.metadata.create_all(bind=engine)
get_db()

# Set up oauth2 scheme
header_scheme = APIKeyHeader(name="x-api-key")

def api_key_auth(api_key: str, db: Session = Depends(get_db)):
    with db.begin():
        hashed_api_keys = get_all_api_keys(db)
        print(f"hashed_api_key: {hashed_api_keys}")

        if not hashed_api_keys:
            logger.info("No API keys found")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No matching API keys found"
            )
        elif not any(verify_password(api_key, hashed_api_key.hashed_api_key) for hashed_api_key in hashed_api_keys):
            logger.info("Invalid API key")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )
# GET /
@app.get("/")
async def root():
    return {"message": "Hello World"}

# CREATE claim
@app.post(
    "/claim_detection/insert", 
    response_model=Optional[BatchClaimResponse],
    responses={
        200: {"description": "Successfully created claims"},
        400: {"description": "Bad request - No claims provided"},
        401: {"description": "Unauthorized - Invalid API key"},
        500: {"description": "Internal server error"}
    },
    status_code=status.HTTP_200_OK
)
async def create_claim_detection_predicts(
    input: SourceDocumentCreate,
    db: Session = Depends(get_db),
    key: str = Depends(header_scheme)
) -> Optional[BatchClaimResponse]:
    """
    Create a claim.
    
    Args:
        input (SourceDocument): Claim input. Example: {text: str}
        db (Session): Database session
    
    Returns:
        Optional[List[Claim]]: A list of claims if found, None otherwise
    """
    try:
        api_key_auth(key, db)
        claim_detection_service = ClaimDetectionService(db, INFERENCE_MODEL_URI)
        return await claim_detection_service.get_predictions(input)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to insert claims: {str(e)}"
        )

@app.post(
    "/claim_detection/update", 
    response_model=Optional[BatchClaimResponse],
    responses={
        200: {"description": "Successfully updated claims"},
        400: {"description": "Bad request - No claims provided"},
        401: {"description": "Unauthorized - Invalid API key"},
        500: {"description": "Internal server error"}
    },
    status_code=status.HTTP_200_OK
)
async def update_claim_detection_predicts(
    claims: List[Claim],
    db: Session = Depends(get_db),
    key: str = Depends(header_scheme)
) -> Optional[BatchClaimResponse]:
    try:
        api_key_auth(key, db)
        if not claims:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No claims provided for update"
            )
        claim_detection_service = ClaimDetectionService(db, INFERENCE_MODEL_URI)
        return await claim_detection_service.update_claims(claims)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update claims: {str(e)}"
        )

@app.get(
    "/claim_detection/get",
    response_model=Optional[List[Claim]],
    responses={
        200: {"description": "Successfully retrieved claims"},
        400: {"description": "Bad request"},
        401: {"description": "Unauthorized - Invalid API key"},
        500: {"description": "Internal server error"}
    },
    status_code=status.HTTP_200_OK
)
async def get_claim_detection(
    start_date: str,
    end_date: str,
    db: Session = Depends(get_db),
    key: str = Depends(header_scheme)
) -> Optional[List[Claim]]:
    try:
        api_key_auth(key, db)
        claim_detection_service = ClaimDetectionService(db, INFERENCE_MODEL_URI)
        return await claim_detection_service.get_claims(start_date, end_date)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get claim detection: {str(e)}"
        )

@app.post(
    "/claim_annotation/insert",
    response_model=Optional[List[ClaimAnnotation]],
    responses={
        200: {"description": "Successfully created annotations"},
        400: {"description": "Bad request - No annotations provided"},
        401: {"description": "Unauthorized - Invalid API key"},
        500: {"description": "Internal server error"}
    },
    status_code=status.HTTP_200_OK
)
async def create_claim_annotations(
    claim_annotation_inputs: BatchClaimAnnotationInput,
    db: Session = Depends(get_db),
    key: str = Depends(header_scheme)
) -> Optional[List[ClaimAnnotation]]:
    """
    Create a claim annotation.
    
    Args:
        claim_annotation_inputs (BatchClaimAnnotationInput): Claim annotation inputs
        db (Session): Database session
    
    Returns:
        Optional[List[ClaimAnnotation]]: A list of claim annotations
    """
    try:
        api_key_auth(key, db)
        if len(claim_annotation_inputs.claims) <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No claim annotation inputs provided"
            )
        claim_annotation_service = ClaimAnnotationService(db)
        return await claim_annotation_service.create_claim_annotation(claim_annotation_inputs)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create claim annotations: {str(e)}"
        )
        
@app.post(
    "/claim_annotation/update",
    response_model=Optional[List[ClaimAnnotation]],
    responses={
        200: {"description": "Successfully updated annotations"},
        400: {"description": "Bad request - No annotations provided"},
        401: {"description": "Unauthorized - Invalid API key"},
        500: {"description": "Internal server error"}
    },
    status_code=status.HTTP_200_OK
)
async def update_claim_annotations(
    claim_annotations: List[ClaimAnnotation],
    db: Session = Depends(get_db),
    key: str = Depends(header_scheme)
) -> Optional[List[ClaimAnnotation]]:
    try:
        api_key_auth(key, db)
        if not claim_annotations:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No claim annotations provided for update"
            )
        claim_annotation_service = ClaimAnnotationService(db)
        return await claim_annotation_service.update_claim_annotation(claim_annotations)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update claim annotations: {str(e)}"
        )

@app.post(
    "/semantic_search/create",
    response_model=Optional[dict],
    responses={
        200: {"description": "Successfully"},
        400: {"description": "Bad request"},
        401: {"description": "Unauthorized - Invalid API key"},
        500: {"description": "Internal server error"}
    },
    status_code=status.HTTP_200_OK
)
async def semantic_search(
    claim_input: SemanticSearchInput,
    db: Session = Depends(get_db),
    key: str = Depends(header_scheme)
) -> Optional[BatchSemanticSearchResponse]:
    try:
        api_key_auth(key, db)
        print(f"claim_input: {claim_input}")
        semantic_search_service = SemanticSearchService(SEMANTIC_SEARCH_URI)
        return await semantic_search_service.get_search_result(claim_input)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get semantic search results: {str(e)}"
        )

@app.get(
    "/claim_model_monitoring/get_data",
    response_model=Optional[List[ClaimModelMonitoring]],
    responses={
        200: {"description": "Successfully retrieved claims"},
        400: {"description": "Bad request"},
        401: {"description": "Unauthorized - Invalid API key"},
        500: {"description": "Internal server error"}
    },
    status_code=status.HTTP_200_OK
)
async def get_claim_model_monitoring_data(
    start_date: str,
    end_date: str,
    db: Session = Depends(get_db),
    key: str = Depends(header_scheme)
) -> Optional[List[ClaimModelMonitoring]]:
    """
    Get claims with inference and annotation by date range
    """
    try:
        api_key_auth(key, db)
        claim_model_monitoring_service = ClaimModelMonitoringService(db)        
        results = claim_model_monitoring_service.get_claims_with_inference_and_annotation(start_date, end_date)
        logger.info(f"results from get_claim_model_monitoring_data: {results}")
        logger.info(f"type of results: {type(results)}")
        return results
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get claim model monitoring data: {str(e)}")

# # READ claim by id or date range
# @app.get("/claim_detection/", response_model=Optional[List[Claim]])
# async def read_claim_text(
#     claim_id: Optional[str] = None,
#     start_date: Optional[str] = None,
#     end_date: Optional[str] = None,
#     db: Session = Depends(get_db)
# ) -> Optional[List[Claim]]:
#     """
#     Read a claim by its ID or by date range.
    
#     Args:
#         claim_id (str): ID of the claim to retrieve
#         start_date (str): Start date of the range
#         end_date (str): End date of the range
#         db (Session): Database session
    
#     Returns:
#         Optional[List[Claim]]: A list of claims if found, None otherwise
#     """
#     if claim_id:
#         try:
#             # Validate claim_id    
#             claim_id = validate_claim_id(claim_id)
            
#             db_text = get_claim_by_id(db=db, claim_id=claim_id)
            
#             if db_text:
#                 return [db_text]
#             else:
#                 return []
#         except Exception as e:
#             raise HTTPException(status_code=500, detail=f"Failed to get claim by ID: {str(e)}")
    
#     elif start_date and end_date:        
#         try:
#             # Validate date range
#             start_date, end_date = validate_date_range(start_date, end_date)
            
#             claims = get_claims_by_created_at(db=db, start_date=start_date, end_date=end_date)
            
#             claims = [claim for claim in claims if len(claim.text) > 0]
#             return claims
#         except Exception as e:
#             raise HTTPException(status_code=500, detail=f"Failed to get claims by date range: {str(e)}")
#     else:
#         raise HTTPException(status_code=400, detail="Either claim_id or start_date and end_date must be provided")

# # UPDATE claim by id
# @app.put("/claim_detection/{claim_id}", response_model=Optional[dict])
# async def update_claim_by_id(
#     claim_id: int, 
#     claim_data: ClaimCreate, # TODO: add validation in case of pydantic ValidationError
#     db: Session = Depends(get_db)
# ) -> Optional[dict]:
#     """
#     Update a claim by its ID.
    
#     Args:
#         claim_id (int): ID of the claim to update
#         claim_data (dict): New claim data (text, label)
#         db (Session): Database session
    
#     Returns:
#         Optional[dict]: A dictionary with a message indicating the update
#     """
#     try:
#         # Validate claim data
#         update_data = claim_data.model_dump()

#         claim = update_claim(db=db, claim_id=claim_id, claim_data=update_data)
        
#         if claim:
#             return {"message": f"Claim at ID={claim.id} updated successfully"}
#         else:
#             raise ValueError(f"Claim ID={claim_id} not found")
#     except ValueError as e:
#         raise HTTPException(status_code=404, detail=f"{str(e)}")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to update claim: {str(e)}")

# # DELETE claim by id
# @app.delete("/claim_detection/{claim_id}", response_model=Optional[dict])
# async def delete_claim_by_id(
#     claim_id: int, 
#     db: Session = Depends(get_db)
# ) -> Optional[dict]:
#     """
#     Delete a claim by its ID.
    
#     Args:
#         claim_id (int): ID of the claim to delete
#         db (Session): Database session
    
#     Returns:
#         Optional[dict]: A dictionary with a message indicating the deletion
#     """
#     try:
#         claim = delete_claim(db=db, claim_id=claim_id)
#         if claim:
#             return {"message": f"Claim at ID={claim_id} deleted successfully"}
#         else:
#             raise ValueError(f"Claim ID={claim_id} not found")
#     except ValueError as e:
#         raise HTTPException(status_code=404, detail=f"{str(e)}")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to delete claim: {str(e)}")