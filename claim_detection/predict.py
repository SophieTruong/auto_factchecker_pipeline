import torch
from transformers import (
    XLMRobertaTokenizer,
    XLMRobertaForSequenceClassification,
)

model_id = "SophieTr/xlm-roberta-base-claim-detection-clef21-24"

# Preprocessing
tokenizer = XLMRobertaTokenizer.from_pretrained(model_id)

# Get model from local disk
model = XLMRobertaForSequenceClassification.from_pretrained("model_id")

def get_sentence_array(doc: str):
    return [str(s) for s in nlp(doc).sents]
    
def predicts(doc: str):
    # Preprocess input text into array of sentences
    sentence_array = get_sentence_array(doc)
    
    # Tokenize sentences in batches
    inputs = tokenizer(
        sentence_array, 
        return_tensors="pt", 
        padding=True, 
        truncation=True
    )
    
    with torch.no_grad():
        logits = model(**inputs).logits
        
    predictions = [logits[i].argmax().item() for i,t in enumerate(logits)]
    
    return sentence_array, predictions