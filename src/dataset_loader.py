import os
import json
from .config import DATASET_PATH, DATASET_CATEGORIES

def load_dataset(category=None):
    """
    Loads datasets based on a specific category.
    If no category is given, loads all datasets in a structured format.
    """
    datasets = {}

    # Check if the data folder exists
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(f"❌ Dataset folder '{DATASET_PATH}' not found.")

    # If a specific category is requested
    if category:
        if category not in DATASET_CATEGORIES:
            raise ValueError(f"❌ Invalid category '{category}'. Available: {list(DATASET_CATEGORIES.keys())}")

        datasets[category] = {}
        for dataset_name in DATASET_CATEGORIES[category]:
            dataset_file = os.path.join(DATASET_PATH, f"{dataset_name}.jsonl")  # Ensure correct file path
            if os.path.exists(dataset_file):
                with open(dataset_file, "r", encoding="utf-8") as f:
                    datasets[category][dataset_name] = [json.loads(line) for line in f]

    # If no category is provided, load all datasets
    else:
        for category, files in DATASET_CATEGORIES.items():
            datasets[category] = {}
            for dataset_name in files:
                dataset_file = os.path.join(DATASET_PATH, f"{dataset_name}.jsonl")  # Ensure correct file path
                if os.path.exists(dataset_file):
                    with open(dataset_file, "r", encoding="utf-8") as f:
                        datasets[category][dataset_name] = [json.loads(line) for line in f]

    return datasets
