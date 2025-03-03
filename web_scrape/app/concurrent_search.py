from typing import Dict
import asyncio
from model import Claim
from google_cse import get_cse_search_results
from politifact import get_politifact_search_results
from translator import translate_claim

from utils import logger

import time
import random

async def concurrent_search(claim: Claim) -> Dict:
    """
    Perform concurrent searches across multiple fact-checking sources
    """
    start_time = time.time()
        
    logger.info(f"Original Claim: {claim}")
    
    english_claim = translate_claim(claim.claim, "en")
    logger.info(f"Translated claim: {english_claim}")
    
    # Create tasks for all searches
    tasks = [
        asyncio.create_task(
            get_politifact_search_results(english_claim, claim.timestamp)
        ),
        asyncio.create_task(
            get_cse_search_results(english_claim, "factcheckorg", claim.timestamp)
        ),
        asyncio.create_task(
            get_cse_search_results(english_claim, "fullfact", claim.timestamp)
        ),
        asyncio.create_task(
            get_cse_search_results(english_claim, "snopes", claim.timestamp)
        )
    ]
    
    # Wait for all searches to complete
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Combine results
    result_dict = {
        "politifact": results[0] if not isinstance(results[0], Exception) else [],
        "factcheck.org": results[1] if not isinstance(results[1], Exception) else [],
        "fullfact": results[2] if not isinstance(results[2], Exception) else [],
        "snopes": results[3] if not isinstance(results[3], Exception) else []
    }
    
    end_time = time.time()
    
    logger.info(f"Time taken: {end_time - start_time} seconds")
    
    return result_dict