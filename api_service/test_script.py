import aiohttp
import asyncio
from typing import Optional, Tuple, Dict, Any, List
import json

class ClaimTestClient:
    def __init__(self, base_url: str = "http://localhost:8080", api_key: Optional[str] = None):
        self.base_url = base_url
        self.headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "api_key": api_key if api_key else ""
        }

    async def test_claim_detection(self, text: str) -> Tuple[Optional[int], Any]:
        """Test claim detection endpoint"""
        url = f"{self.base_url}/claim_detection/insert"
        payload = {"text": text}

        return await self._make_request(url, payload)

    async def test_claim_annotation(self, claims: list) -> Tuple[Optional[int], Any]:
        """Test claim annotation endpoint"""
        url = f"{self.base_url}/claim_annotation/insert"
        payload = {"claims": claims}

        return await self._make_request(url, payload)

    async def test_semantic_search(self, claims: List[str]) -> Tuple[Optional[int], Any]:
        """Test semantic search endpoint"""
        url = f"{self.base_url}/semantic_search/create"
        payload = {"claims": claims}
        
        return await self._make_request(url, payload)

    async def _make_request(self, url: str, payload: Dict) -> Tuple[Optional[int], Any]:
        """Make HTTP request and handle response"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=self.headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        print("Success! Response:", json.dumps(result, indent=2))
                    else:
                        print(f"Error: {response.status}")
                        print("Response:", await response.text())
                    return response.status, await response.json()
        except Exception as e:
            print(f"Request failed: {str(e)}")
            return None, str(e)

async def main():
    # Test data
    test_text = """Yhdysvaltain presidentti Donald Trump kävi keskiviikkona puhelinkeskustelut Venäjän presidentti Vladimir Putinin sekä Ukrainan presidentti Volodymyr Zelenskyin kanssa. Trumpin mukaan presidentit keskustelivat neuvottelujen aloittamisesta sodan lopettamiseksi Ukrainassa. Trump sanoi neuvottelujen alkavan välittömästi."""
    
    test_claims = [
        {
            "source_document_id": "d7ab92ba-28ae-4392-9dcc-564a78ca3e9a",
            "claim_id": "e9d96424-401e-49e8-baa4-acd9bf519de8",
            "claim_text": "Yhdysvaltain presidentti Donald Trump kävi keskiviikkona puhelinkeskustelut Venäjän presidentti Vladimir Putinin sekä Ukrainan presidentti Volodymyr Zelenskyin kanssa.",
            "binary_label": True,
            "text_label": ""
        },
        {
            "source_document_id": "d7ab92ba-28ae-4392-9dcc-564a78ca3e9a",
            "claim_id": "b2e54b98-3428-4be1-8847-b31a7ee34ce4",
            "claim_text": "Trumpin mukaan presidentit keskustelivat neuvottelujen aloittamisesta sodan lopettamiseksi Ukrainassa.",
            "binary_label": False,
            "text_label": ""
        },
        {
            "source_document_id": "d7ab92ba-28ae-4392-9dcc-564a78ca3e9a",
            "claim_id": "b0e43bd9-dd29-4548-89fc-9b615f5a99e6",
            "claim_text": "Trump sanoi neuvottelujen alkavan välittömästi.",
            "binary_label": False,
            "text_label": ""
        }
    ]

    test_semantic_claims = [
        "Ydysvaltain presidentti Donald Trump kävi keskiviikkona puhelinkeskustelut Venäjän presidentti Vladimir Putinin sekä Ukrainan presidentti Volodymyr Zelenskyin kanshsa.",
        "Covid is a hoax"
    ]

    # Initialize client
    client = ClaimTestClient(api_key="1addab1395546324")

    # Test claim detection
    print("\nTesting claim detection:")
    await client.test_claim_detection(test_text)

    # Test claim annotation
    print("\nTesting claim annotation:")
    await client.test_claim_annotation(test_claims)

    # Test semantic search
    print("\nTesting semantic search:")
    await client.test_semantic_search(test_semantic_claims)

if __name__ == "__main__":
    asyncio.run(main())