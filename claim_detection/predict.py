import torch
from transformers import (
    XLMRobertaTokenizer,
    XLMRobertaForSequenceClassification,
)

import spacy
from spacy.language import Language

# Preprocessing
tokenizer = XLMRobertaTokenizer.from_pretrained("FacebookAI/xlm-roberta-base", cache_dir="xml-roberta-model")

# Get model from local disk
model = XLMRobertaForSequenceClassification.from_pretrained("SophieTr/xlm-roberta-base-claim-detection-clef21-24", cache_dir="xml-roberta-model")

@Language.component("set_custom_boundaries")
def set_custom_boundaries(doc):
    for token in doc[:-1]:
        if token.text in [".", "?", "!"]:
            doc[token.i+1].is_sent_start = True
        else:
            doc[token.i+1].is_sent_start = False
    return doc

nlp = spacy.load("fi_core_news_sm")
nlp.add_pipe("set_custom_boundaries", before="parser")

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