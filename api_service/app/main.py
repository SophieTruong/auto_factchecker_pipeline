"""
Reference source for streaming response:
https://medium.com/@ab.hassanein/streaming-responses-in-fastapi-d6a3397a4b7b
"""
from typing import List, Optional, Annotated

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

# Streaming response
from sse_starlette import EventSourceResponse

from fastapi.security import APIKeyHeader

from sqlalchemy.orm import Session

# Import pydantic models
from models.claim import Claim
from models.claim_detection_response import BatchClaimResponse
from models.source_document import SourceDocumentCreate
from models.claim_annotation_input import BatchClaimAnnotationInput
from models.claim_annotation import ClaimAnnotation
from models.semantic_search_input import SemanticSearchInputs
from models.pipeline_metrics_response import PipelineMetricsResponse

# Import database models
from database.postgres import engine, Base, get_db
from database.crud import get_all_api_keys

# Import services
from services import ClaimDetectionService
from services.pipeline_metrics_monitoring import PipelineMetricsMonitoringService
from services.evidence_retrieval_service import EvidenceRetrievalService

# Import utils
from utils.app_logging import logger
from utils.password_hashing import verify_password

# Setup logging
logger.info('API is starting up')

# Set up FastAPI
app = FastAPI()
origins = ["*"] # TODO: Restrict to only allowed origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["GET", "POST"], 
    allow_headers=["*"], # TODO: Restrict to only allowed headers
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
            
async def semantic_search_callback(claim_input: SemanticSearchInputs):
    
    # Create the service with lazy initialization
    evidence_service = EvidenceRetrievalService()
    
    # Connections will be established on first use
    for claim in claim_input.claims:
        
        try:
            # Send data to RCP server
            result = await evidence_service.process_search_request(claim)
            
            yield result
        
        except Exception as e:
        
            logger.error(f"Error processing claim {claim.claim}: {e}")
            # Continue with other claims even if one fails
            continue
        
# GET /
@app.get("/")
async def root(
    db: Session = Depends(get_db),
    key: str = Depends(header_scheme)
):
    api_key_auth(key, db)
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
        
        claim_detection_service = ClaimDetectionService()
        
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
        
        claim_detection_service = ClaimDetectionService()
        
        return await claim_detection_service.update_predictions(claims)
    
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
        claim_detection_service = ClaimDetectionService()
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
        claim_detection_service = ClaimDetectionService()
        return await claim_detection_service.create_claim_annotation(claim_annotation_inputs)
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
        claim_detection_service = ClaimDetectionService()
        return await claim_detection_service.update_claim_annotation(claim_annotations)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update claim annotations: {str(e)}"
        )

@app.post(
    "/semantic_search/create",
    response_class=EventSourceResponse,
    responses={
        200: {"description": "Successfully"},
        400: {"description": "Bad request"},
        401: {"description": "Unauthorized - Invalid API key"},
        500: {"description": "Internal server error"}
    },
    status_code=status.HTTP_200_OK
)
       
async def semantic_search_queue(
    claim_input: SemanticSearchInputs,
    db: Session = Depends(get_db),
    key: str = Depends(header_scheme)
):
    try:
        api_key_auth(key, db)
        # text/event-stream        
        return EventSourceResponse(semantic_search_callback(claim_input), media_type="text/event-stream")
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get semantic search results: {str(e)}"
        )

@app.get(
    "/pipeline_metrics",
    response_model=Optional[PipelineMetricsResponse],
    responses={
        200: {"description": "Successfully retrieved claims"},
        400: {"description": "Bad request"},
        401: {"description": "Unauthorized - Invalid API key"},
        500: {"description": "Internal server error"}
    },
    status_code=status.HTTP_200_OK
)
async def get_pipeline_metrics(
    start_date: str,
    end_date: str,
    db: Session = Depends(get_db),
    key: str = Depends(header_scheme)
) -> Optional[PipelineMetricsResponse]:
    """
        Get claims with inference and annotation by date range
    """
    try:
        api_key_auth(key, db)
        pipeline_metrics_service = PipelineMetricsMonitoringService(start_date, end_date)        
        results = await pipeline_metrics_service.get_pipeline_metrics()
        logger.info(f"results from get_pipeline_metrics: {results}")
        logger.info(f"type of results: {type(results)}")
        return results
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get pipeline metrics: {str(e)}")