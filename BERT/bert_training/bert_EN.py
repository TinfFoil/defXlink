from datasets import load_dataset, Dataset, DatasetDict
from transformers import AutoTokenizer, DataCollatorWithPadding, TrainingArguments, AutoModelForSequenceClassification, Trainer
import numpy as np
from datasets import load_metric
import pandas as pd


# From tsv to pandas once again
train = pd.read_csv('/home/mmartinelli/huggingface/wiki_train.tsv', sep='\t', header=0)
validate = pd.read_csv('/home/mmartinelli/huggingface/wiki_validate.tsv', sep='\t', header=0)
test = pd.read_csv('/home/mmartinelli/huggingface/wiki_test.tsv', sep='\t', header=0)


# Format dataset for Huggingface
train_dataset = Dataset.from_pandas(train)
validate_dataset = Dataset.from_pandas(validate)
test_dataset = Dataset.from_pandas(test)
dict_data = {"train": train_dataset, "validation": validate_dataset, "test": test_dataset}

raw_datasets = DatasetDict(dict_data)
checkpoint = 'bert-base-cased'
tokenizer = AutoTokenizer.from_pretrained(checkpoint)

def tokenize_function(dataset):
    return tokenizer(dataset['sentence'], truncation=True)

tokenized_datasets = raw_datasets.map(tokenize_function, batched=True)
data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

def compute_metrics(eval_preds):
    metric = load_metric("glue", "mrpc")
    logits, labels = eval_preds
    predictions = np.argmax(logits, axis=-1)
    return metric.compute(predictions=predictions, references=labels)

training_args = TrainingArguments("test-trainer", evaluation_strategy="epoch")
model = AutoModelForSequenceClassification.from_pretrained(checkpoint, num_labels=2)

trainer = Trainer(
        model,
        training_args,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["validation"],
        data_collator=data_collator,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics,
)

trainer.train()

model.save_pretrained('/home/mmartinelli/huggingface/saved_model_EN/')
