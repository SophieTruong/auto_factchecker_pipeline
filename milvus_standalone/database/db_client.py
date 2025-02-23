import os   
import dotenv
import time
from pymilvus import connections, model
from pymilvus.exceptions import MilvusException

dotenv.load_dotenv()

_HOST = os.getenv('HOST')
_PORT = os.getenv('PORT')
print(f"HOST: {_HOST}")
print(f"PORT: {_PORT}")

MODEL = 'msmarco-distilbert-base-dot-prod-v3'

sentence_transformer_ef = model.dense.SentenceTransformerEmbeddingFunction(
    model_name=MODEL, # Specify the model name
    device='cpu' # Specify the device to use, e.g., 'cpu' or 'cuda:0'
)


# Create a Milvus connection
def create_connection(max_retries=5, retry_delay=5):
    print(f"\nCreate connection...")
    for attempt in range(max_retries):
        try:
            conn = connections.connect(host=_HOST, port=_PORT)
            return conn
        
        except MilvusException as e:
            print(f"Error: {e}")
            if attempt == max_retries - 1:
                raise e
            print(f"Connection attempt {attempt + 1} failed. URI: f{_HOST}:{_PORT}. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
