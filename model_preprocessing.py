# Import libraries
from datasets import Dataset
import pandas as pd
import numpy as np
from pathlib import Path
import csv


# Build Pandas dataframe to feed the model with Navigli's (cleaned) good and bad instances
wiki_good = pd.read_csv("wiki_good.tsv", sep="\t")
wiki_bad = pd.read_csv("wiki_bad.tsv", sep="\t")

frames = [wiki_good, wiki_bad]
wiki_dataframe = pd.concat(frames)
#print(wiki_dataframe)
#shuffled_data = wiki_dataframe.sample(frac = 1)
#print("shuffled", shuffled_data)

train, validate, test = \
        np.split(wiki_dataframe.sample(frac = 1, random_state = 42), [int(.8 * len(wiki_dataframe)), int(.9 * len(wiki_dataframe))])

train.to_csv("wiki_train.tsv", sep="\t", index_label="idx")
validate.to_csv("wiki_validate.tsv", sep="\t", index_label="idx")
test.to_csv("wiki_test.tsv", sep="\t", index_label="idx")

# Format dataset for Huggingface
train_dataset = Dataset.from_pandas(train)
validate_dataset = Dataset.from_pandas(validate)
test_dataset = Dataset.from_pandas(test)
split_dataset = {"train": train_dataset, "validation": validate_dataset, "test": test_dataset}
print(split_dataset)
#print(split_dataset["validation"][('LABEL')])
path = Path('/home/mmartinelli/huggingface/')
doc = 'train_val_test.tsv'
with open(doc, 'wb') as tsvfile:
    fieldnames = ['train', 'validation', 'test']
    dict_writer = csv.DictWriter(tsvfile, fieldnames=fieldnames, delimiter='\t')
    dict_writer.writeheader()
    dict_writer.writerows(split_dataset)
