import aiohttp
import asyncio
import time
from typing import List
import statistics
BASE_URL = "http://model_inference:8080"

async def wait_for_service():
    max_retries = 30
    retry_count = 0
    
    async with aiohttp.ClientSession() as session:
        while retry_count < max_retries:
            try:
                async with session.get(f"{BASE_URL}/health") as response:
                    if response.status == 200:
                        print("Service is ready!")
                        return True
            except aiohttp.ClientError:
                print(f"Service not ready, attempt {retry_count + 1}/{max_retries}")
                retry_count += 1
                await asyncio.sleep(1)
        return False

async def make_request(session, text: List[str]=["Test sentence"]) -> float:
    start_time = time.time()
    async with session.post(
        f"{BASE_URL}/predict",
        json=text
    ) as response:
        await response.json()
        return time.time() - start_time

async def load_test(num_requests: int, concurrent_requests: int):
    async with aiohttp.ClientSession() as session:
        tasks: List[asyncio.Task] = []
        response_times: List[float] = []
        
        for _ in range(num_requests):
            if len(tasks) >= concurrent_requests:
                done, pending = await asyncio.wait(
                    tasks, 
                    return_when=asyncio.FIRST_COMPLETED
                )
                response_times.extend([task.result() for task in done])
                tasks = list(pending)  # Convert set back to list
            
            print(f"type(tasks): {type(tasks)}")
            try:
                test_sentence_array = [
                    "Test sentence",
                    "Toimeentulotukea on maksettu yli 100 000 nuorelle.",
                    "Kelan tutkijan Tuija Korpelan mukaan koulutuspolitiikan ja työvoimapolitiikan tavoitteet ovat osin ristiriidassa.",
                    "Ilman ammatillista koulutusta oleva nuori saa työttömyystukea, jos hakee opiskelupaikkoja ja ottaa paikan vastaan.",
                    "Koska ensimmäisen kerran hakijoita suositaan, moni nuori ei ota vähemmän mieluista opiskelupaikkaa vastaan tai jättää hakematta, jos ei ehdi valmistautua pääsykokeeseen.",
                    "Korpelan mukaan osalla nuorista on mielenterveysongelmia ja silloin he tarvitsisivat enemmän tukipalveluita kuin rankaisua siitä, että eivät hae työ- tai opiskelupaikkaa.",
                    "Miksi 18–24-vuotiaat nuoret aikuiset ovat yliedustettuina toimeentulotuen saajissa?",
                    "Toimeentulotukiuudistusta valmistellut virkamiestyöryhmä julkisti keskiviikkona loppumuistionsa.",
                    "Siitä selvisi, että vuonna 2023 perustoimeentulotukea oli maksettu 106 000 nuorelle aikuiselle.",
                    "Donald Trumps is the new US president",
                    ]
                new_task = asyncio.create_task(
                    make_request(session, test_sentence_array)
                )
                tasks.append(
                    new_task
                )
            except Exception as e:
                print(f"Error creating task: {e}")
                break
        
        # Wait for remaining tasks
        if tasks:
            done, _ = await asyncio.wait(tasks)
            response_times.extend([task.result() for task in done])
        
        return response_times

async def main():
    num_requests = 100
    concurrent_requests = 10
    if not await wait_for_service():
        print("Service failed to start")
        return

    print(f"Starting load test with {num_requests} total requests, {concurrent_requests} concurrent...")
    response_times = await load_test(num_requests, concurrent_requests)

    # Calculate statistics
    avg_time = statistics.mean(response_times)
    max_time = max(response_times)
    min_time = min(response_times)
    p95 = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
    
    print(f"\nResults:")
    print(f"Average response time: {avg_time:.2f}s")
    print(f"Max response time: {max_time:.2f}s")
    print(f"Min response time: {min_time:.2f}s")
    print(f"95th percentile: {p95:.2f}s")
    print(f"Requests per second: {num_requests/sum(response_times):.2f}")
    
if __name__ == "__main__":
    asyncio.run(main())