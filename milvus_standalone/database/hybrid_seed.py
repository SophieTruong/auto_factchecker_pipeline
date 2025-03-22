from pymilvus import utility, model

from pymilvus.model.hybrid import BGEM3EmbeddingFunction

from hybrid_retrieval import HybridRetriever

from seed_data_processing import merge_all_data

import time

from datetime import datetime

import argparse

import os

import dotenv

dotenv.load_dotenv(dotenv.find_dotenv())

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(f"Logger: {logger}")

parser = argparse.ArgumentParser()
parser.add_argument("--test", type=str)
args = parser.parse_args()

S_TRANSFORMERS_MDL_DIR = os.getenv("S_TRANSFORMERS_MDL_DIR")

def main():
    
    dense_ef = BGEM3EmbeddingFunction(
        model_name="BAAI/bge-m3",
        device="cpu",
        normalize_embeddings=True,
        cache_dir=S_TRANSFORMERS_MDL_DIR,
    )
    
    # MODEL = 'msmarco-MiniLM-L6-cos-v5' # normalize_embedding

    # sentence_transformer_ef = model.dense.SentenceTransformerEmbeddingFunction(
    #     model_name=MODEL, # Specify the model name'
    #     normalize_embeddings=True,
    #     query_instruction = "",
    #     doc_instruction = "",
    #     device='cpu', # Specify the device to use, e.g., 'cpu' or 'cuda:0'
    #     cache_folder=S_TRANSFORMERS_MDL_DIR,
    # )
    
    start_time = time.time()
    
    logger.info(f"Start time: {start_time}")
    
    standard_retriever = HybridRetriever(
        uri="http://milvus_standalone:19530",
        collection_name="milvus_hybrid",
        dense_embedding_function=dense_ef,
        # dense_embedding_function=sentence_transformer_ef,
    )

    # Merge all data
    df = merge_all_data()

    # Shuffle data
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    if args.test == "1":
        df = df.head(30000)
    
    logger.info(f"IN SEEDING df.shape: {df.shape}")

    # Process data
    ids = df.id.values
    
    docs = df.text.values
    
    truncate_docs = [doc[:60000] for doc in docs] # max length of varchar in milvus for text field
            
    labels = df.label.values
    
    sources = df.source.values
    
    urls = df.url.values
    
    created_ats = [utility.mkts_from_datetime(created_at) for created_at in df.created_at.values]
    
    data = [
        {
            "id": str(ids[i]),
            "text": truncate_docs[i],
            "label": labels[i],
            "source": sources[i],
            "url": urls[i],
            "created_at": created_ats[i],
        }
        for i in range(len(truncate_docs))
    ]
    
    logger.info(f"Length of data to be inserted: {len(data)}")

    # Insert data into Milvus
    
    standard_retriever.drop_collection()
    
    standard_retriever.build_collection()
    
    # for meta_data in data:
    #     standard_retriever.insert_data(meta_data["text"], meta_data)
    
    for i in range(0, len(data), 1000):
        batch = data[i:i+1000]
        batch_end = min(i+1000, len(data))
        try:
            logger.info(f"Inserting batch {i//1000 + 1}: records {i} to {batch_end}")
            inserted_results = standard_retriever.batch_insert_data(batch)
            logger.info(f"Successfully inserted {len(batch)} records. Result: {inserted_results}")
        except Exception as e:
            logger.error(f"Error inserting batch {i//1000 + 1} (records {i} to {batch_end})")
            logger.error(f"Exception details: {str(e)}")
            logger.error(f"Batch size: {len(batch)} records")
            # Continue with the next batch - no need to increment i as the loop will do that
            continue
            
    
    end_time = time.time()
    logger.info(f"End time: {end_time}")
    logger.info(f"Time taken to insert data: {end_time - start_time} seconds")
    
    # Search
    logger.info("Testing search...")
    
    query = "Russia attacked Ukraine in 2022"
    
    logger.info(f"Query: {query}")
    
    logger.info("Dense search...")
    results = standard_retriever.search(query, k=10, mode="dense")
    logger.info(results)
    
    time.sleep(10)

    logger.info("Sparse search...")
    results = standard_retriever.search(query, k=10, mode="sparse")
    logger.info(results)
    
    time.sleep(10)
                
    logger.info("Hybrid search...")
    results = standard_retriever.search(query, k=10, mode="hybrid")
    logger.info(results)
    
    time.sleep(10)
    
    logger.info("Testing filter...")
    
    filter = "created_at <= {created_at}"
    filter_params = {"created_at": utility.mkts_from_datetime(datetime(2021, 1, 1))}
    
    results = standard_retriever.search(query, k=10, mode="hybrid", filter=filter, filter_params=filter_params)
    
    logger.info(results)
    
    for result in results:
        logger.info(utility.hybridts_to_datetime(result["created_at"]))

if __name__ == "__main__":
    main()