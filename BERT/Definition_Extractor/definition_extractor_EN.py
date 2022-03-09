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

model = AutoModelForSequenceClassification.from_pretrained('/home/mmartinelli/huggingface/saved_model/')

pipe = TextClassificationPipeline(model=model, tokenizer=tokenizer, return_all_scores=True)

predictions = pipe(sentences)

final_scores = []

#print highest score in list of sentences using pre-trained model bert trained with Navigli's corpus
for idx, sentence in enumerate(sentences):
    scores = predictions[idx][1]['score']
    final_scores.append((sentence, scores))

sorted_scores = sorted(final_scores, key=itemgetter(1))
#print(sorted_scores)

highest_score = sorted_scores[-1]
print('highest score:', highest_score)
