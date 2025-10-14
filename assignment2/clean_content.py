# USER GUIDE: From sudo-code-2025, `cd` into assignment_2 and run `python clean_content.py`

from multiprocessing import Pool, cpu_count
import json

import sys
sys.path.append("..")

from preprocess.data_cleaner import clean_item, process_segmented_content

from UITws_v1.UITws_v1 import UITws_v1 # For VN word segmentation

if __name__ == "__main__":
    # Load the dataset
    with open(file="../data/processed/news_dataset.json",
              mode="r",
              encoding="utf-8") as file:
        data: list = json.load(file)
    
    # Load or assume `data` is already defined
    with Pool(cpu_count() - 2) as pool:
        # Distribute the work across all available CPU cores
        cleaned_data: list = pool.map(clean_item, data)
        
    # Extract contents from cleaned_data
    contents = [item['content'] for item in cleaned_data]

    # Segment each content into words
    uitws_v1 = UITws_v1("../UITws_v1/checkpoints/base_long_sep_sfx.pkl")
    segmented_sample_content = uitws_v1.segment(texts=contents,
                                            pre_tokenized=False,
                                            batch_size=128)
    
    # Post-processing the segmented content before re-merging them into the data
    segmented_content = [item[0][0].split()
                         for item in segmented_sample_content
                         if item and item[0] and item[0][0]]
    processed_segmented_content = process_segmented_content(segmented_content)
    
    # Merge the processed_segmented_content into the cleaned_data
    for item, segmented in zip(cleaned_data, processed_segmented_content):
        item['content'] = segmented

    # Save results to JSON
    with open("../data/processed/cleaned_news_dataset.json", "w", encoding="utf-8") as file:
        json.dump(cleaned_data, file, ensure_ascii=False, indent=2)