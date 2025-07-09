# IndicEval-Indian-Multilingual-Evalution-framework(Benchmark)

This project is designed to evaluate different models (such as Lalama 3 and Gemini 2.0) on various datasets (UPSC, NEET, JEE) using multiple prompting strategies like zero-shot, few-shot, and chain-of-thought (CoT).

---

## 📂 Project Structure

```
Benchmark/
├── data/              # Datasets used for evaluation
├── logs/              # Log files
├── results/           # Evaluation results (by model & strategy)
├── src/               # Source code (including config.py)
    |___benchmark.py
    |___config.py  
    |___dataset_loader.py  
    |___model_api.py  
    |___post_process.py            
    |___view_metrics.py  
├── run_benchmark.py   # Main script to run evaluations
├── test_api.py        # Script to test API connections
├── .gitignore         # Git ignored files
```

---

## 🚀 Features

- Supports multiple models: Lalama 3, Gemini 2.0, and more.
- Supports multiple evaluation strategies: zero-shot, few-shot, chain-of-thought.
- Logs and saves evaluation results in structured folders.
- Easily configurable through `src/config.py`.

---

## 🔑 Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/your-username/your-repo-name.git
cd Benchmark
```

### 2. Create and configure `.env`
```
TOGETHER_API_KEY=your_together_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

👉 **Never share your real `.env` file publicly.**

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

---

## ⚙️ Running the Benchmark

```bash
python run_benchmark.py
```

To test APIs:
```bash
python test_api.py
```

---

## 📊 Results

Results are automatically saved in the `/results` directory, organized by model, strategy, and dataset.

---

## 📝 License

This project is open-source and free to use for educational and research purposes.

---

## 🙏 Acknowledgements

- Together AI
- Google Gemini API
- Scikit-learn
- Python Dotenv

