import asyncio
import aiohttp
import time
import json

# URL of your LoadBalancer Service
API_URL = "http://<EXTERNAL-IP>/v1/chat/completions"
API_KEY = "EMPTY"

prompts = [
    "Explain the theory of relativity in 50 words.",
    "Write a Python function to reverse a linked list.",
    "What is the capital of Australia?",
    "Optimize this SQL query: SELECT * FROM users;",
    "Write a haiku about GPUs."
] * 10  # 50 requests total

async def send_request(session, prompt, req_id):
    payload = {
        "model": "Qwen/Qwen3-235B-A22B-Instruct",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 128,
        "temperature": 0.7
    }
    start = time.time()
    try:
        async with session.post(API_URL, json=payload, headers={"Authorization": f"Bearer {API_KEY}"}) as resp:
            result = await resp.json()
            latency = time.time() - start
            print(f"[{req_id}] Status: {resp.status} | Latency: {latency:.2f}s")
            return latency
    except Exception as e:
        print(f"[{req_id}] Error: {e}")
        return 0

async def benchmark():
    async with aiohttp.ClientSession() as session:
        tasks = [send_request(session, p, i) for i, p in enumerate(prompts)]
        start_total = time.time()
        latencies = await asyncio.gather(*tasks)
        total_time = time.time() - start_total
        
        # Stats
        valid_latencies = [l for l in latencies if l > 0]
        avg_lat = sum(valid_latencies) / len(valid_latencies)
        tps_est = (len(prompts) * 128) / total_time # Rough tokens per second estimate
        
        print(f"\n--- Benchmark Results (3 Replicas / 12 GPUs) ---")
        print(f"Total Requests: {len(prompts)}")
        print(f"Total Time: {total_time:.2f}s")
        print(f"Avg Latency: {avg_lat:.2f}s")
        print(f"Throughput (Requests/sec): {len(prompts)/total_time:.2f}")

if __name__ == "__main__":
    asyncio.run(benchmark())
