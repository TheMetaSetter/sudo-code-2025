from typing import List
from multiprocessing import Pool, cpu_count

def convert_ner_results_into_words(ner_result):
    """
    This function converts NER result of a single sentence into words.
    """
    
    sentence_token = ""
    for e in ner_result:
        if "##" in e["word"]:
            sentence_token = sentence_token + e["word"].replace("##","")
        elif e["entity"] =="I":
            sentence_token = sentence_token + "_" + e["word"]
        else:
            sentence_token = sentence_token + " " + e["word"]
    return sentence_token.split()

def segment_sentences_into_words(
    sentences: list[str],
    nlp_pipeline,
) -> List[str]:
    """
    Segment a sentence into words.
    
    Args:
    - sentence: str - the input sentence
    - nlp_pipeline: pipeline object created by the
    pipeline function (`from transformers import pipeline`)

    Returns:
    - List of word tokens for the sentence.
    """

    ner_results = nlp_pipeline(sentences)
    
    # Do not use all the CPUs since it will cause local deadlock.
    with Pool(cpu_count() - 3) as pool:
        words_for_each_sentences = pool.map(
            convert_ner_results_into_words,
            ner_results)

    processed_sentences = words_for_each_sentences
    
    return processed_sentences