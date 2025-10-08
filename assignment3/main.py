import os
import glob
import random
import sys
import time

sys.path.append("..")

from preprocess.word_segmentor import segment_sentences_into_words
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
from gensim.models import Word2Vec

# === Paths and data loading ===
data_path = "../data/raw/viwik18/dataset"
filename_list = sorted(os.listdir(data_path))

# Construct full paths for each file
filepath_list = [os.path.join(data_path, filename) for filename in filename_list]

# Pattern for data files
file_pattern = os.path.join(data_path, "viwik18_*")

# Collect and concatenate all data files
files = sorted(glob.glob(file_pattern))
all_bytes = b"".join(open(f, "rb").read() for f in files)
text = all_bytes.decode("utf-8")

# Split and clean text
split_text = text.split("  ")
cleaned_splits = [s.strip() for s in split_text if s.strip()]

# === Random sampling ===
random.seed(42)
randomized_splits = random.sample(cleaned_splits, 100)

# === Model setup ===
tokenizer = AutoTokenizer.from_pretrained("NlpHUST/vi-word-segmentation")
model = AutoModelForTokenClassification.from_pretrained("NlpHUST/vi-word-segmentation")
nlp = pipeline("token-classification", model=model, tokenizer=tokenizer)

# === Word segmentation ===
start_time = time.time()
sentences = segment_sentences_into_words(cleaned_splits, nlp)
end_time = time.time()

print(f"Time taken: {end_time - start_time:.2f} seconds")

# === Train and save Word2Vec model ===
model = Word2Vec(
    sentences,
    vector_size=100,
    window=5,
    min_count=5,
    workers=4,
)
model.save("../word2vec.model")