import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import together
import google.generativeai as genai
from .config import TOGETHER_API_KEY, GEMINI_API_KEY

# API Clients
client = together.Together(api_key=TOGETHER_API_KEY)
genai.configure(api_key=GEMINI_API_KEY)

# Models
TOGETHER_MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo"
GEMINI_MODEL = "gemini-2.0-flash"

# Config
MAX_WORKERS = 20  # Threads for parallel execution
GEMINI_SLEEP_TIME = 5  # Sleep between requests (optional, adjust as needed)
TOGETHER_SLEEP_TIME = 2

# Query Gemini API
def query_gemini(prompt):
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(prompt)
        
        # Extract the response content safely
        if response and response.candidates:
            return response.candidates[0].content.parts[0].text.strip()
        else:
            return "No response"
    except Exception as e:
        print(f"[Gemini] API Error: {e}")
        return "N/A"

# Query Together AI API
def query_together(prompt):
    try:
        response = client.chat.completions.create(
            model=TOGETHER_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content.strip() if response.choices else "No response"
    except Exception as e:
        print(f"[Together AI] API Error: {e}")
        return "N/A"

# Generic Multi-thread Runner
# def run_multithread(prompts, query_fn, sleep_time=0):
#     results = []
#     with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
#         futures = []

#         for idx, prompt in enumerate(prompts):
#             prompt_with_id = f"Q{idx+1}:\n{prompt}"  # Add index prefix for tracking
#             futures.append(executor.submit(query_fn, prompt_with_id))
#             if sleep_time > 0:
#                 time.sleep(sleep_time)  # Avoid rate limits

#         for future in as_completed(futures):
#             results.append(future.result())

#     return results

# def run_multithread(prompts, query_fn, sleep_time=0):
#     results = [None] * len(prompts)
#     with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
#         futures = {}
#         for idx, prompt in enumerate(prompts):
#             prompt_with_id = f"Q{idx+1}:\n{prompt}"
#             future = executor.submit(query_fn, prompt_with_id)
#             futures[future] = idx
#             if sleep_time > 0:
#                 time.sleep(sleep_time)

#         for future in as_completed(futures):
#             idx = futures[future]
#             results[idx] = future.result()

#     return results

def run_multithread(prompts, query_fn, sleep_time=0):
    results = [None] * len(prompts)
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {}
        for idx, prompt in enumerate(prompts):
            future = executor.submit(query_fn, prompt)
            futures[future] = idx
            if sleep_time > 0:
                time.sleep(sleep_time)

        for future in as_completed(futures):
            idx = futures[future]
            results[idx] = future.result()

    return results


# Benchmark Execution
def batch_query(prompts):
    print(f"Total Prompts: {len(prompts)} | Max Threads: {MAX_WORKERS}\n")

    print("Running with Gemini...\n")
    all_gemini_results = run_multithread(prompts, query_gemini, sleep_time=GEMINI_SLEEP_TIME)

    print("Gemini Done!\nRunning with Together AI...\n")
    all_together_results = run_multithread(prompts, query_together, sleep_time=TOGETHER_SLEEP_TIME)

    print("Benchmark Completed!\n")

    return {
        "gemini": all_gemini_results,
        "together": all_together_results
    }
