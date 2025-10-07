import json
from preprocess.vn_validator import validate_and_fix_vietnamese_text
from preprocess.text_normalizer import (
    strip_html,
    normalize_spacing,
    remove_code_artifacts
)
from multiprocessing import Pool, cpu_count

path_to_raw_data = "./data/raw/news_dataset.json"

with open(path_to_raw_data, "r") as data_file:
    data = json.load(data_file)
    
def preprocess_content(content: str) -> str:
    # Normalize content into Unicode NFC
    content = validate_and_fix_vietnamese_text(content)[0]
    
    # Remove HTML tags
    content = strip_html(content)
    
    # Normalize spacing
    content = normalize_spacing(content)
    
    # Remove common code artifacts
    content = remove_code_artifacts(content)
    
    return content

# Preprocess all JSON in data using multiprocessing for speed
def preprocess_item(item: dict) -> dict:
    # First, we preprocess the main content of each piece of news.
    preprocessed_item: dict = {}
    preprocessed_item["content"] = preprocess_content(item["content"])
    
    # Topic is treated as the label for later classification task.
    preprocessed_item["topic"] = item["topic"]
    
    # Then, we store the metadata of each piece of news.
    metadata_fields = ["source", "topic", "crawled_at"]
    preprocessed_item["metadata"]: dict = {field: item[field] for field in metadata_fields}
    
    return preprocessed_item

import time

def main() -> None:
    with open(path_to_raw_data, "r") as data_file:
        data = json.load(data_file)

    start_time = time.time()

    with Pool(int(cpu_count() / 4)) as pool:
        processed_data = pool.map(preprocess_item, data)

    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"Preprocessed {len(processed_data)} articles in {elapsed_time:.2f} seconds.")
    with open("./data/processed/news_dataset.json", "w") as out_file:
        json.dump(processed_data, out_file, ensure_ascii=False, indent=4)
    print("Saved preprocessed data to ./data/processed/news_dataset.json")

if __name__ == "__main__":
    main()