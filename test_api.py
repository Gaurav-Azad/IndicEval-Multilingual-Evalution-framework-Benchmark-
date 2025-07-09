import google.generativeai as genai
import os

# Load API key
GEMINI_API_KEY = ""
genai.configure(api_key=GEMINI_API_KEY)

def query_gemini(prompt):
    """Queries Gemini model and returns the response."""
    model = genai.GenerativeModel("gemini-2.0-flash")  # Change to "gemini-1.5-pro" if needed
    response = model.generate_content(prompt)
    
    return response.text if response else "Error: No response"

# Example test
if __name__ == "__main__":
    print(query_gemini("What is the capital of India?"))
