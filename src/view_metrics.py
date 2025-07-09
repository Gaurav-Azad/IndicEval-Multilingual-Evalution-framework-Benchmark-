import os
import json
import csv
from sklearn.metrics import precision_score, recall_score, confusion_matrix

from .config import RESULTS_PATH, LOG_PATH


def view_metrics():
    if not os.path.exists(RESULTS_PATH):
        print("❌ No benchmark results found. Run the benchmark first.")
        return

    log_data = []
    structured_results = {}

    print(f"🔍 Checking Results Directory: {RESULTS_PATH}")

    for model_name in os.listdir(RESULTS_PATH):
        model_path = os.path.join(RESULTS_PATH, model_name)
        if not os.path.isdir(model_path):
            continue

        print(f"📂 Found Model: {model_name}")
        structured_results[model_name] = {}

        for prompt_type in os.listdir(model_path):
            prompt_path = os.path.join(model_path, prompt_type)
            if not os.path.isdir(prompt_path):
                continue

            print(f"   📂 Found Prompting Type: {prompt_type}")
            structured_results[model_name][prompt_type] = {}

            for file_name in os.listdir(prompt_path):
                if not file_name.endswith(".json"):
                    continue

                dataset_name = file_name.replace(".json", "")
                dataset_file = os.path.join(prompt_path, file_name)

                print(f"      📄 Processing Dataset: {dataset_name}")

                with open(dataset_file, "r", encoding="utf-8") as f:
                    dataset_results = json.load(f)

                correct_count = sum(1 for item in dataset_results if item["is_correct"])
                total_questions = len(dataset_results)
                accuracy = (correct_count / total_questions) * 100 if total_questions > 0 else 0

                # Extract binary ground truth and predictions
                y_true = [1 if item["predicted_answer"] == item["correct_answer"] else 0 for item in dataset_results]
                y_pred = [1 if item["is_correct"] else 0 for item in dataset_results]

                # Calculate precision, recall, and confusion matrix
                try:
                    precision = precision_score(y_true, y_pred, zero_division=0) * 100
                    recall = recall_score(y_true, y_pred, zero_division=0) * 100
                    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
                except Exception as e:
                    precision = recall = tn = fp = fn = tp = 0
                    print(f"⚠️ Metrics calculation failed for {dataset_name}: {e}")

                # Save metrics
                structured_results[model_name][prompt_type][dataset_name] = {
                    "accuracy": accuracy,
                    "precision": precision,
                    "recall": recall,
                    "tp": tp,
                    "tn": tn,
                    "fp": fp,
                    "fn": fn
                }

                log_data.append(
                    f"{model_name} | {prompt_type} | {dataset_name} "
                    f"=> Accuracy: {accuracy:.2f}%, Precision: {precision:.2f}%, Recall: {recall:.2f}%, TP: {tp}, FP: {fp}, FN: {fn}, TN: {tn}"
                )

    # Save log.txt
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "w", encoding="utf-8") as log_file:
        log_file.write("\n".join(log_data))

    print(f"\n✅ Evaluation Completed. Results saved in {LOG_PATH}")

    save_csv(structured_results)


def save_csv(structured_results):
    csv_path = LOG_PATH.replace(".txt", ".csv")

    with open(csv_path, "w", newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Model", "Prompt Type", "Dataset", "Accuracy", "Precision", "Recall", "TP", "FP", "FN", "TN"])

        for model in structured_results:
            for prompt_type in structured_results[model]:
                for dataset, metrics in structured_results[model][prompt_type].items():
                    writer.writerow([
                        model,
                        prompt_type,
                        dataset,
                        f"{metrics['accuracy']:.2f}",
                        f"{metrics['precision']:.2f}",
                        f"{metrics['recall']:.2f}",
                        metrics['tp'],
                        metrics['fp'],
                        metrics['fn'],
                        metrics['tn']
                    ])

    print(f"✅ CSV Results saved at {csv_path}")
