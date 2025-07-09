import os
import json
from src.dataset_loader import load_dataset
from src.model_api import batch_query   
from src.post_process import extract_option_label  
from src.view_metrics import view_metrics  
from .config import RESULTS_PATH, STRATEGY_MODE



def format_prompt(question, options, strategy, dataset=None, k=3, current_index=0):
    """Formats the prompt based on the selected strategy and language."""
    options_text = "\n".join(options)

    # Language detection: check if question is in Hindi (Devanagari script)
    def is_hindi(text):
        return any('\u0900' <= ch <= '\u097F' for ch in text)

    is_hindi_lang = is_hindi(question)

    if strategy == "zero-shot":
        instruction = (
            "कृपया (a, b, c, या d) में से एक उत्तर चुनें। उत्तर:"
            if is_hindi_lang else
            "Answer with A, B, C, or D:"
        )
        return f"{question}\nOptions:\n{options_text}\n{instruction}"

    elif strategy == "few-shot":
        assert dataset is not None, "Dataset required for few-shot prompting."
        few_shot_examples = []
        count = 0

        for idx, example in enumerate(dataset):
            if idx == current_index:
                continue  # Skip current question

            example_lang = is_hindi(example['question'])
            instruction = (
                "उत्तर:" if example_lang else "Answer:"
            )

            formatted_example = (
                f"Q: {example['question']}\nOptions:\n" +
                "\n".join(example["options"]) +
                f"\n{instruction} {example['label']}"
            )
            few_shot_examples.append(formatted_example)
            count += 1
            if count >= k:
                break

        instruction_final = (
            "उत्तर:" if is_hindi_lang else "Answer:"
        )

        few_shot_prompt = "\n\n".join(few_shot_examples)
        return f"{few_shot_prompt}\n\nQ: {question}\nOptions:\n{options_text}\n{instruction_final}"

    elif strategy == "cot":
        instruction = (
            "कृपया चरण दर चरण सोचें और फिर (a, b, c, या d) में से उत्तर दें:"
            if is_hindi_lang else
            "Think step by step and then answer with A, B, C, or D:"
        )
        return f"{question}\nOptions:\n{options_text}\n{instruction}"

    else:
        raise ValueError("Invalid prompting strategy.")


def process_dataset(category):
    """Processes a dataset using batch processing for multiple models."""
    datasets = load_dataset(category)
    results = {}

    strategies = ["zero-shot", "few-shot", "cot"] if STRATEGY_MODE == "all" else [STRATEGY_MODE]

    # Process each dataset separately (for example, UPSC English and UPSC Hindi)
    for dataset_name in datasets.get(category, []):
        dataset = datasets[category][dataset_name]
        
        all_prompts = []
        all_prompt_metadata = []  # (dataset_name, strategy, question_index)

        # Collect prompts for the current dataset and strategies
        for strategy in strategies:
            for index, item in enumerate(dataset):
                formatted_prompt = format_prompt(
                    item["question"], item["options"], strategy, dataset=dataset, current_index=index
                )
                # Unique identifier for each prompt
                prompt_with_id = f"Q_{category}_{dataset_name}_{strategy}_{index + 1}:\n{formatted_prompt}"
                all_prompts.append(prompt_with_id)
                all_prompt_metadata.append((category, dataset_name, strategy, index))

        # Run batch once for this dataset only
        model_responses = batch_query(all_prompts)

        # Reorganize results per model
        for model_name, responses in model_responses.items():
            per_model_data = {}

            for i, (category, dataset_name, strategy, index) in enumerate(all_prompt_metadata):
                dataset = datasets[category][dataset_name]
                item = dataset[index]

                predicted_label = extract_option_label(responses[i], item["options"], strategy) if responses[i] else "N/A"
                is_correct = predicted_label == item["label"].lower()

                result_entry = {
                    "question": item["question"],
                    "model": model_name,
                    "model_answer": responses[i],
                    "correct_answer": item["label"],
                    "predicted_answer": predicted_label,
                    "is_correct": is_correct,
                    "strategy": strategy,
                }

                # Structure results by category, dataset, and strategy
                if category not in per_model_data:
                    per_model_data[category] = {}
                if dataset_name not in per_model_data[category]:
                    per_model_data[category][dataset_name] = {}
                if strategy not in per_model_data[category][dataset_name]:
                    per_model_data[category][dataset_name][strategy] = []
                per_model_data[category][dataset_name][strategy].append(result_entry)

            # Save to files for the current dataset
            for category, category_data in per_model_data.items():
                for dataset_name, strat_data in category_data.items():
                    for strategy, entries in strat_data.items():
                        result_dir = os.path.join(RESULTS_PATH, model_name, strategy)
                        os.makedirs(result_dir, exist_ok=True)
                        result_path = os.path.join(result_dir, f"{dataset_name}.json")
                        with open(result_path, "w", encoding="utf-8") as f:
                            json.dump(entries, f, indent=4, ensure_ascii=False)

            results[model_name] = per_model_data

    return results




def run_benchmark():
    """Runs benchmarking sequentially for different dataset categories (one at a time)."""
    categories = ["Law"]  # Add more categories if needed "UPSC,Physics,Law,Biology"

    final_results = {}

    for category in categories:
        print(f"🔍 Processing category: {category}...")
        result = process_dataset(category)
        final_results[category] = result

    print(f"✅ Benchmarking completed! Results saved in {RESULTS_PATH}")

    # Compute and display accuracy metrics
    view_metrics()

if __name__ == "__main__":
    run_benchmark()
