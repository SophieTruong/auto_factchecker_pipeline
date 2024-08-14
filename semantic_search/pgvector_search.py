from sentence_transformers import SentenceTransformer

model = SentenceTransformer('msmarco-distilbert-base-dot-prod-v3')

def get_sentence_transformers_encode(query):
    return model.encode(query)
