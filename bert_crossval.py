from datasets import load_dataset, Dataset, DatasetDict
from transformers import AutoTokenizer, DataCollatorWithPadding, TrainingArguments, AutoModelForSequenceClassification, Trainer
import numpy as np
from datasets import concatenate_datasets, load_metric
import pandas as pd


# From tsv to pandas once again
fold1 = pd.read_csv('/home/mmartinelli/huggingface/abc/fold1.tsv', sep='\t', header=0)
fold2 = pd.read_csv('/home/mmartinelli/huggingface/abc/fold2.tsv', sep='\t', header=0)
fold3 = pd.read_csv('/home/mmartinelli/huggingface/abc/fold3.tsv', sep='\t', header=0)
fold4 = pd.read_csv('/home/mmartinelli/huggingface/abc/fold4.tsv', sep='\t', header=0)
fold5 = pd.read_csv('/home/mmartinelli/huggingface/abc/fold5.tsv', sep='\t', header=0)
fold6 = pd.read_csv('/home/mmartinelli/huggingface/abc/fold6.tsv', sep='\t', header=0)
fold7 = pd.read_csv('/home/mmartinelli/huggingface/abc/fold7.tsv', sep='\t', header=0)
fold8 = pd.read_csv('/home/mmartinelli/huggingface/abc/fold8.tsv', sep='\t', header=0)
fold9 = pd.read_csv('/home/mmartinelli/huggingface/abc/fold9.tsv', sep='\t', header=0)
fold10 = pd.read_csv('/home/mmartinelli/huggingface/abc/fold10.tsv', sep='\t', header=0)



# Format dataset for Huggingface
#train_dataset = Dataset.from_pandas(train)
#validate_dataset = Dataset.from_pandas(validate)
#test_dataset = Dataset.from_pandas(test)
#dict_data = {"train": train_dataset, "validation": validate_dataset, "test": test_dataset}


fold1_dataset = Dataset.from_pandas(fold1)
fold2_dataset = Dataset.from_pandas(fold2)
fold3_dataset = Dataset.from_pandas(fold3)
fold4_dataset = Dataset.from_pandas(fold4)
fold5_dataset = Dataset.from_pandas(fold5)
fold6_dataset = Dataset.from_pandas(fold6)
fold7_dataset = Dataset.from_pandas(fold7)
fold8_dataset = Dataset.from_pandas(fold8)
fold9_dataset = Dataset.from_pandas(fold9)
fold10_dataset = Dataset.from_pandas(fold10)

checkpoint = 'bert-base-cased'
tokenizer = AutoTokenizer.from_pretrained(checkpoint)

def tokenize_function(dataset):
    return tokenizer(dataset['sentence'], truncation=True)

folds = [fold1_dataset,fold2_dataset,fold3_dataset,fold4_dataset,fold5_dataset,fold6_dataset,fold7_dataset,fold8_dataset,fold9_dataset,fold10_dataset]

data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

def compute_metrics(eval_preds):
    metric = load_metric("glue", "mrpc")
    logits, labels = eval_preds
    predictions = np.argmax(logits, axis=-1)
    return metric.compute(predictions=predictions, references=labels)


for idx, fold in enumerate(folds):
    if idx == 0:
        train_dataset = concatenate_datasets(folds[1:])
    elif idx == 9:
        train_dataset = concatenate_datasets(folds[:-1])
    else:
        train_dataset = concatenate_datasets(folds[:idx]+folds[idx+1:])
    
    temp_dict = {"train": train_dataset, "validation": fold}
    crossval_dict = DatasetDict(temp_dict)
    crossval_dict = crossval_dict.map(tokenize_function, batched=True)
    training_args = TrainingArguments("test-trainer", evaluation_strategy="epoch")
    model = AutoModelForSequenceClassification.from_pretrained(checkpoint, num_labels=2)

    trainer = Trainer(
            model,
            training_args,
            train_dataset=crossval_dict["train"],
            eval_dataset=crossval_dict["validation"],
            data_collator=data_collator,
            tokenizer=tokenizer,
            compute_metrics=compute_metrics,
            )
    
    trainer.train()
