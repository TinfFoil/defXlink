from datasets import load_dataset, Dataset, DatasetDict
from transformers import AutoTokenizer, TextClassificationPipeline, DataCollatorWithPadding, AutoModelForSequenceClassification
import numpy as np
from datasets import load_metric
import pandas as pd
import spacy
from operator import itemgetter

#load spacy to sentencize (tokenize with sentences)
nlp = spacy.load("en_core_web_md")
nlp.add_pipe("sentencizer")

sentences = []

#choose a path to get a file
path_to_text = input("Enter the path to the text:\n")

#open file, sentencize and create list of sentences
with open(path_to_text, 'r') as f:
    f = f.read()
    doc = nlp(f)
    sentences = [str(sent) for sent in list(doc.sents)]


checkpoint = 'bert-base-cased'
tokenizer = AutoTokenizer.from_pretrained(checkpoint)
model = AutoModelForSequenceClassification.from_pretrained('/home/mmartinelli/huggingface/saved_model_EN/')

pipe = TextClassificationPipeline(model=model, tokenizer=tokenizer, return_all_scores=True)

#predictions = pipe(subdump_list)
predictions = pipe(sentences)

final_scores = []
n=0

#print highest score in list of sentences using pre-trained model bert trained with Navigli's corpus
for idx, sentence in enumerate(sentences):
    scores = predictions[idx][1]['score']
    if scores >= 0.6:
        n = n + 1
        final_scores.append((sentence, scores))
        if n == 2:
            break

print(final_scores)
