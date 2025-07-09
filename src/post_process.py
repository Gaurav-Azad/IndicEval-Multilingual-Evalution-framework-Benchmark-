import re

def extract_option_label(prediction, options, strategy):
    prediction = prediction.strip().lower()

    def normalize(label):
        return re.sub(r'[^\w]', '', label.lower())  # removes (, ), whitespace etc.

    # Define regex patterns for English and Hindi answer formats
    patterns = [
        r'final answer\s*is\s*\$?\\?boxed\{?([a-e])\}?',
        r'answer\s*(is|:)?\s*\(?([a-e])\)?',
        r'option\s*\(?([a-e])\)?\s*(is\s*correct|is\s*true|is\s*the\s*answer)?',
        r'(उत्तर|सही\s*विकल्प)\s*(है|:)?\s*\(?([a-e])\)?'
    ]

    for pattern in patterns:
        match = re.search(pattern, prediction, re.IGNORECASE)
        if match:
            for group in match.groups()[::-1]:
                if group and group.lower() in ['a', 'b', 'c', 'd','e']:
                    return normalize(group)

    # Chain-of-thought: Check the last line for a valid answer
    if strategy == 'cot':
        last_line = prediction.strip().split('\n')[-1]

        cot_patterns = [
            r'answer\s*(is|:)?\s*\(?([a-e])\)?',
            r'(उत्तर|सही\s*विकल्प)\s*(है|:)?\s*\(?([a-e])\)?',
            r'\(?([a-e])\)?'  # Loose match for standalone letter
        ]

        for pattern in cot_patterns:
            match = re.search(pattern, last_line, re.IGNORECASE)
            if match:
                for group in match.groups()[::-1]:
                    if group and group.lower() in ['a', 'b', 'c', 'd','e']:
                        return normalize(group)

    # Fallback: Match based on actual content of options
    option_map = {}

    for opt in options:
        if ")" in opt:
            parts = opt.split(")", 1)
        elif "." in opt:
            parts = opt.split(".", 1)
        else:
            print(f"⚠️ Warning: Unknown option format: {opt}")
            continue

        if len(parts) == 2:
            key = parts[1].strip().lower()
            val = parts[0].strip().lower()
            option_map[key] = val

    for key, value in option_map.items():
        if key in prediction:
            return normalize(value)

    # Last fallback → any standalone letter a-d
    match = re.search(r'\(?([a-e])\)?', prediction, re.IGNORECASE)
    if match:
        return normalize(match.group(1))

    return None

