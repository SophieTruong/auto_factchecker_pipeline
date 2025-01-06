from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Import pydantic models
from models.claim_input import ClaimInput
from models.claim import Claim, ClaimCreate

# Import database models
from database.postgres import engine, Base, SessionLocal
from database.crud import insert_claims, get_claim_by_id, get_claims_by_created_at, update_claim, delete_claim

from sqlalchemy.orm import Session

from utils import validate_claim_id, validate_date_range

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

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CREATE claim
# TODO: replace dummy claim detection logic with model inference
@app.post("/claim_detection/insert_claims", response_model=Optional[List[Claim]])
async def create_claim_detection_predicts(
    input: ClaimInput, # TODO: add validation in case of pydantic ValidationError
    db: Session = Depends(get_db)
) -> Optional[List[Claim]]:
    """
    Create a claim.
    
    Args:
        input (ClaimInput): Claim input. Example: {text: str}
        db (Session): Database session
    
    Returns:
        Optional[List[Claim]]: A list of claims if found, None otherwise
    """
    try:
        text = input.text
        
        # Split text into claims
        claims = [{'text': str(t), 'label': True} for t in text.split(".") if len(t) > 0]

        bulk_insert_res = insert_claims(db,claims)
        
        return bulk_insert_res
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to insert claims: {str(e)}"
        )

# READ claim by id or date range
@app.get("/claim_detection/", response_model=Optional[List[Claim]])
async def read_claim_text(
    claim_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
) -> Optional[List[Claim]]:
    """
    Read a claim by its ID or by date range.
    
    Args:
        claim_id (str): ID of the claim to retrieve
        start_date (str): Start date of the range
        end_date (str): End date of the range
        db (Session): Database session
    
    Returns:
        Optional[List[Claim]]: A list of claims if found, None otherwise
    """
    if claim_id:
        try:
            # Validate claim_id    
            claim_id = validate_claim_id(claim_id)
            
            db_text = get_claim_by_id(db=db, claim_id=claim_id)
            
            if db_text:
                return [db_text]
            else:
                return []
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get claim by ID: {str(e)}")
    
    elif start_date and end_date:        
        try:
            # Validate date range
            start_date, end_date = validate_date_range(start_date, end_date)
            
            claims = get_claims_by_created_at(db=db, start_date=start_date, end_date=end_date)
            
            claims = [claim for claim in claims if len(claim.text) > 0]
            return claims
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get claims by date range: {str(e)}")
    else:
        raise HTTPException(status_code=400, detail="Either claim_id or start_date and end_date must be provided")

# UPDATE claim by id
@app.put("/claim_detection/{claim_id}", response_model=Optional[dict])
async def update_claim_by_id(
    claim_id: int, 
    claim_data: ClaimCreate, # TODO: add validation in case of pydantic ValidationError
    db: Session = Depends(get_db)
) -> Optional[dict]:
    """
    Update a claim by its ID.
    
    Args:
        claim_id (int): ID of the claim to update
        claim_data (dict): New claim data (text, label)
        db (Session): Database session
    
    Returns:
        Optional[dict]: A dictionary with a message indicating the update
    """
    try:
        # Validate claim data
        update_data = claim_data.model_dump()

        claim = update_claim(db=db, claim_id=claim_id, claim_data=update_data)
        
        if claim:
            return {"message": f"Claim at ID={claim.id} updated successfully"}
        else:
            raise ValueError(f"Claim ID={claim_id} not found")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=f"{str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update claim: {str(e)}")

# DELETE claim by id
@app.delete("/claim_detection/{claim_id}", response_model=Optional[dict])
async def delete_claim_by_id(
    claim_id: int, 
    db: Session = Depends(get_db)
) -> Optional[dict]:
    """
    Delete a claim by its ID.
    
    Args:
        claim_id (int): ID of the claim to delete
        db (Session): Database session
    
    Returns:
        Optional[dict]: A dictionary with a message indicating the deletion
    """
    try:
        claim = delete_claim(db=db, claim_id=claim_id)
        if claim:
            return {"message": f"Claim at ID={claim_id} deleted successfully"}
        else:
            raise ValueError(f"Claim ID={claim_id} not found")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=f"{str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete claim: {str(e)}")