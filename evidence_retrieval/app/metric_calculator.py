import statistics   

from typing import Dict, Any

def compute_metrics(result_json: Dict[str, Any]) -> Dict[str, Any]:
    
    claim_text = result_json['claim']
    
    # Produce the metrics logs      
    vector_db_search_scores_fb = [value["score"] for value in result_json['vector_db_results']["facebook_post"]]
    
    vector_db_search_scores_news = [value["score"] for value in result_json['vector_db_results']["facebook_post"]]
    
    vector_db_search_scores = vector_db_search_scores_fb + vector_db_search_scores_fb
    
    vector_db_search_size = len(vector_db_search_scores)
                
    vector_db_search_scores_min = min(vector_db_search_scores) if vector_db_search_scores else 0
    
    vector_db_search_scores_max = max(vector_db_search_scores) if vector_db_search_scores else 0
    
    vector_db_search_scores_mean = sum(vector_db_search_scores) / (vector_db_search_size if vector_db_search_size > 0 else 1)
    
    vector_db_search_scores_median = statistics.median(vector_db_search_scores) if vector_db_search_size > 0 else 0
    
    web_search_cosine_similarity = [value["similarity"] for value in result_json['web_search_results']]
    
    web_search_size = len(web_search_cosine_similarity)
                
    web_search_cosine_similarity_min = min(web_search_cosine_similarity) if web_search_cosine_similarity else 0
    
    web_search_cosine_similarity_max = max(web_search_cosine_similarity) if web_search_cosine_similarity else 0
    
    web_search_cosine_similarity_mean = sum(web_search_cosine_similarity) / (web_search_size if web_search_size > 0 else 1)
    
    web_search_cosine_similarity_median = statistics.median(web_search_cosine_similarity) if web_search_size > 0 else 0

    return {
        "claim_text": claim_text,
        "vector_db_search_size": vector_db_search_size,
        "vector_db_search_scores_min": vector_db_search_scores_min,
        "vector_db_search_scores_max": vector_db_search_scores_max,
        "vector_db_search_scores_mean": vector_db_search_scores_mean,
        "vector_db_search_scores_median": vector_db_search_scores_median,
        "web_search_size": web_search_size,
        "web_search_cosine_similarity_min": web_search_cosine_similarity_min,
        "web_search_cosine_similarity_max": web_search_cosine_similarity_max,
        "web_search_cosine_similarity_mean": web_search_cosine_similarity_mean,
        "web_search_cosine_similarity_median": web_search_cosine_similarity_median
    }