import torch
from transformers import (
    XLMRobertaTokenizer,
    XLMRobertaForSequenceClassification,
)

import spacy

# Preprocessing
tokenizer = XLMRobertaTokenizer.from_pretrained("FacebookAI/xlm-roberta-base", cache_dir="xml-roberta-model")

# Get model from local disk
model = XLMRobertaForSequenceClassification.from_pretrained("SophieTr/xlm-roberta-base-claim-detection-clef21-24", cache_dir="xml-roberta-model")

nlp = spacy.load("fi_core_news_sm")

sentencizer = nlp.add_pipe("sentencizer")

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