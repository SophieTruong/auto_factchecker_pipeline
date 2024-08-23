from sentence_transformers import SentenceTransformer

MODEL = 'msmarco-distilbert-base-dot-prod-v3'

model = SentenceTransformer(MODEL,
                            cache_folder='./sentence-transformer-model')

def get_sentence_transformers_encode(query):
    return model.encode(query)
