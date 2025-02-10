import aiohttp
from typing import Dict, List
from fastapi import HTTPException

async def make_request(url: str, start_date: str, end_date: str) -> Dict:
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
            async with session.get(
                url, 
                params={"start_date": start_date, "end_date": end_date}, 
                headers = {'accept': 'application/json'}
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise HTTPException(
                        status_code=response.status,
                        detail=f"Model inference failed: {error_text}"
                    )
                
                return await response.json()
                
    except aiohttp.ClientError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to connect to monitoring service: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Request failed: {str(e)}"
        )
