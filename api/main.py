from fastapi import Depends, FastAPI, HTTPException

from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session

from claim_detection.predict import predicts
from pgvector_search import get_sentence_transformers_encode
from postgres import SessionLocal, engine
import crud, models, schemas

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
models.Base.metadata.create_all(bind=engine)
# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def root():
    return {"message": "Hello World"}

# CREATE
@app.post("/claim_detection/insert_claims", response_model=list[schemas.Claim])
def create_claim_detection_predicts(input: schemas.Input, db: Session = Depends(get_db)):
    """
    This function calls the claim detection model and saves model inputs and outputs to the Claim DB
    Args:
        input (schemas.Input): Long text string as input of the claim detection pipeline
        db (Session): a Claim DB session 
    Returns:
        If DB insertion successes, return the inserted data; else, throws a 404 error code. 
    """
    # TODO: does input.text has length limit? E.g., data validation
    
    # calls the claim detection model
    sent_arr, pred_arr = predicts(input.text)
    
    claim_io_array = [{ "text": t.strip(),
                        "label": l
                       } for (t,l) in list(zip(sent_arr, pred_arr))]
            
    try:
        bulk_insert_res = crud.insert_claims(db,claim_io_array)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"{e}")
    
    return bulk_insert_res

# READ
@app.get("/claim_detection/{id}", response_model=schemas.Claim)
def read_claim_text(id: int, db: Session = Depends(get_db)):
    """
    The function looks up a Claim detection model output by ID
    Args:
        id (int): ID of claim for DB lookup
        db (Session): a Claim DB session 
    Returns:
        If ID is found from the Claim DB; else, throws a 404 error code. 
    """
    db_text = crud.get_claim_by_id(db, id=id)
    
    if db_text is None:
        raise HTTPException(status_code=404, detail=f"Claim with ID={id} not found")
    
    return db_text

# READ
@app.get("/fact_checked_text/{id}", response_model=schemas.TextEmbedding)
def read_fact_checked_text(id: int, db: Session = Depends(get_db)):
    db_text = crud.get_text(db, id=id)
    
    if db_text is None:
        raise HTTPException(status_code=404, detail=f"Text with ID={id} not found")
    
    return db_text

# READ
@app.post("/fact_checked_text", response_model=list[schemas.TextEmbedding])
def create_semantic_search_text(input: schemas.Input, db: Session = Depends(get_db)):
    encoded_vector = get_sentence_transformers_encode(input.text)
    
    found_rows = crud.get_texts_by_embeddings(db,encoded_vector)
    similar_texts = [x[0] for x in found_rows]
    
    if similar_texts is None or len(similar_texts) == 0:
        raise HTTPException(status_code=404, detail=f"No similar text is found from the database.")
    
    return similar_texts

# CREATE
@app.post("/fact_checked_text/insert_text", response_model=schemas.TextEmbedding)
def create_fact_checked_text(input: schemas.TextEmbeddingCreate, db: Session = Depends(get_db)):
    encoded_vector = get_sentence_transformers_encode(input.text)
    input_embedding = input.model_dump()
    try:
        fact_checked_text = crud.insert_embedding(db,input_embedding,encoded_vector)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"{e}")
    
    return fact_checked_text

# CREATE
@app.post("/fact_checked_text/insert_texts", response_model=list[schemas.TextEmbedding])
def create_fact_checked_texts(input_arr: list[schemas.TextEmbeddingCreate], db: Session = Depends(get_db)):
    encoded_vector = get_sentence_transformers_encode([input.text for input in input_arr])
    input_embedding_arr = [input.model_dump() for input in input_arr]
    try:
        bulk_insert_res = crud.insert_embeddings(db,input_embedding_arr, encoded_vector)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"{e}")
    
    return bulk_insert_res

# UPDATE
@app.patch("/fact_checked_text/{id}", response_model=schemas.TextEmbedding)
def update_fact_checked_text(id: int, text_embedding_update: schemas.TextEmbeddingCreate, db: Session = Depends(get_db)):
    update_data = text_embedding_update.model_dump(exclude_unset=True)

    try:
        update_res = crud.update_embedding(db,id,update_data)
        if len(update_res) == 0:
            raise HTTPException(status_code=404, detail=f"Text embedding data with ID={id} not found")
    
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"{e}")
    
    return update_res[0]

# DELETE
@app.delete("/fact_checked_text/{user_id}", response_model=dict)
def delete_fact_checked_text(id: int, db: Session = Depends(get_db)):
    
    try:
        delete_data = crud.delete_embedding(db,id)
        
        if len(delete_data) == 0:
            raise HTTPException(status_code=404, detail=f"Text embedding data with ID={id} not found")

    except Exception as e:
        raise HTTPException(status_code=404, detail=f"{e}")

    response = f"Text embedding at ID={delete_data[0]} deleted successfully"
    return {"message": response}
