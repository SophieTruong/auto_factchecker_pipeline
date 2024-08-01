from pydantic import BaseModel

from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from predict import predicts


app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Input(BaseModel):
    text: str
    
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/")
async def get_claim_detection_result(input: Input):
    sent_arr, pred_arr = predicts(input.text)
    
    ret = {}
    for i, sent in enumerate(sent_arr):
        ret[i] = {
            "text": sent.strip(),
            "prediction": pred_arr[i]
        }
        
    return ret