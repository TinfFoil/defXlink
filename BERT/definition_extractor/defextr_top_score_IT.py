from sentence_splitter import SentenceSplitter, split_text_into_sentences
from datasets import load_dataset, Dataset, DatasetDict
from transformers import AutoTokenizer, TextClassificationPipeline, DataCollatorWithPadding, AutoModelForSequenceClassification
import numpy as np
from datasets import load_metric
import pandas as pd
from operator import itemgetter


#choose a path to get a file
path_to_text = input("Enter the path to the text:\n")

splitter = SentenceSplitter(language='it')
#open file, sentencize and create list of sentences
with open(path_to_text, 'r') as f:
    f = f.read()
    sentences = splitter.split(text=f)



checkpoint = 'bert-base-multilingual-cased'
tokenizer = AutoTokenizer.from_pretrained(checkpoint)

model = AutoModelForSequenceClassification.from_pretrained('/home/mmartinelli/huggingface/saved_model_IT/')

pipe = TextClassificationPipeline(model=model, tokenizer=tokenizer, return_all_scores=True)


predictions = pipe(sentences)

final_scores = []

#print highest score in list of sentences using pre-trained model bert trained with Navigli's corpus
for idx, sentence in enumerate(sentences):
    scores = predictions[idx][1]['score']
    final_scores.append((sentence, scores))
    
print(final_scores)

sorted_scores = sorted(final_scores, key=itemgetter(1))
print('number of sentences:', len(sorted_scores))


highest_score = sorted_scores[-1]
print('highest score:', highest_score)



