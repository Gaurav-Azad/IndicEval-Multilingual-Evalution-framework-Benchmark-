import os
from dotenv import load_dotenv

# Load environment variables from .env in the project root
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

# API Keys loaded from environment
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Base Directory: Move one level up to project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Paths relative to the root directory
DATASET_PATH = os.path.join(BASE_DIR, "data")
RESULTS_PATH = os.path.join(BASE_DIR, "results")
LOG_PATH = os.path.join(BASE_DIR, "logs", "evaluation_log.txt")

STRATEGY_MODE = "few-shot"

DATASET_CATEGORIES = {
    "UPSC": ["upsc", "upsc_hindi"],
    "Physics": ["neet_physics", "neet_hindi_physics"],
    "Chemistry": ["neet_chemistry"],
    "Biology": ["neet_biology", "neet_hindi_biology"],
    "Law": ["lsat_lr"],
}

# Ensure directories exist
os.makedirs(os.path.dirname(RESULTS_PATH), exist_ok=True)
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
