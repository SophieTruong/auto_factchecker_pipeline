import aiohttp
from typing import Optional, Dict, List, Union

class RequestException(Exception):
    """Base exception for request failures"""
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"Request failed with status {status_code}: {detail}")

async def make_request(url: str, data: Optional[Union[Dict, List]]) -> Dict:
    """
    Make an async HTTP POST request and return the response data.
    
    Args:
        url (str): The endpoint URL
        data (Dict | List): The data to send
        
    Returns:
        Dict: The response data
        
    Raises:
        HTTPException: If request fails
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise RequestException(
                        status_code=response.status,
                        detail=f"Web search failed: {error_text}"
                    )
                
                return await response.json()
                
    except aiohttp.ClientError as e:
        raise RequestException( 
            status_code=503,
            detail=f"Failed to connect to web search service: {str(e)}"
        )
    except Exception as e:
        raise RequestException(
            status_code=500,
            detail=f"Request failed: {str(e)}"
        )
