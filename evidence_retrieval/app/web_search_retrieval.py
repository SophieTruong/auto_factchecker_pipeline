from deep_translator import GoogleTranslator

import string
import re
import json
from datetime import datetime

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)

import spacy

nlp = spacy.load("en_core_web_md")

# Custom JSON encoder to handle datetime objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def english_text_preprocessing(text: str) -> str:
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(text)
    filtered_text = [word for word in word_tokens if word not in stop_words]
    
    # Lemmatize using spaCy
    doc = nlp(" ".join(filtered_text))
    lemmatized_text = [token.lemma_ for token in doc]
    
    # Join lemmatized words
    processed_text = " ".join(lemmatized_text)
    
    return processed_text

    
def calculate_tf_idf(preprocessed_texts: list, query_text: str) -> dict:
    """
    Calculate TF-IDF vectors for preprocessed texts and query, and return similarity scores
    
    Args:
        preprocessed_texts: List of preprocessed text strings
        query_text: The query text to compare against
        
    Returns:
        Dictionary with similarity scores for each text
    """
    # Include the query in the corpus for vectorization
    all_texts = preprocessed_texts.copy()
    
    # Preprocess the query
    processed_query = english_text_preprocessing(query_text)
    all_texts.append(processed_query)
    
    # Vectorize all texts
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(all_texts)
    
    # Get the query vector (last element)
    query_vector = tfidf_matrix[-1]
    
    # Get document vectors (all except the last one)
    doc_vectors = tfidf_matrix[:-1]
    
    # Calculate cosine similarity between query and each document
    if doc_vectors.shape[0] > 0:
        similarities = cosine_similarity(query_vector, doc_vectors).flatten()
    else:
        similarities = []
    
    # Return results as a dictionary
    results = {
        "similarities": similarities,
        "vectorizer": vectorizer,
        "query_vector": query_vector,
        "doc_vectors": doc_vectors
    }
    
    return results

def rank_web_search_results(web_search_results: dict, top_k: int = 10) -> dict:
    
    query_text = web_search_results["claim"]
    
    # translate the query text to english
    translated_query_text = GoogleTranslator(source='auto', target='en').translate(query_text)
    
    text_keys = {
        "politifact": "statement",
        "factcheck.org": ["snippet", "title"],
        "fullfact": ["snippet", "title"],
        "snopes": ["snippet", "title"]
    }
    
    # preprocess the text
    processed_text_list = []
    result_mapping = []  # Store mapping between processed text index and original result
    
    for key, result_list in web_search_results["response"].items():
        for result in result_list:
            result["source"] = key
            if key == "politifact":
                result["processed_text"] = english_text_preprocessing(result["statement"])
            else:
                title_snippet_combined = result["title"] + " " + result["snippet"]
                result["processed_text"] = english_text_preprocessing(title_snippet_combined)
                
            processed_text_list.append(result["processed_text"])
            result_mapping.append(result)
            
    # Calculate Tf-Idf and similarities
    tf_idf_results = calculate_tf_idf(processed_text_list, translated_query_text)
    similarities = tf_idf_results["similarities"]
    
    # Create ranked results with similarity scores
    ranked_results = []
    for i, similarity in enumerate(similarities):
        ranked_results.append({
            "result": result_mapping[i],
            "similarity": float(similarity)  # Convert to Python float for JSON serialization
        })
    
    # Sort the results based on the similarity
    ranked_results.sort(key=lambda x: x["similarity"], reverse=True)
    
    # Return the top k results with all metadata
    top_k_results = ranked_results[:top_k]
    return top_k_results
