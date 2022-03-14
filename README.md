# defXlink

defXlink is a project that branches into two objectives:
- Automatic definitional context extraction for Wikipedia articles
- Automatic definitions linking for food recipes

These involve the Italian and English languages.

## Premises: Build your Own Wikipedia Corpus

In order to use the BERT models as definition extractors, you first need a tailor-made corpus, possibly from Wikipedia (or not really, it's your call).
The folder `corpora` contains four Python files. `wiki_parser_EN.py` is the code to parse the English dump of Wikipedia to extract food-related Wikipedia articles. It works by searching for specific categories. If you want to use it to create your ad-hoc corpus, you only need to define a list of categories, the code does the rest. Please, bear in mind that you need to specify a directory that can be accessed for parsing and a directory where you'd like to save your articles. Each article will be cleaned from noise (as much as possible), specifically from the 'See also' section until the bottom. If you want to keep everything, just comment those lines.

## Definitional Context Extraction

Two trained BERT models are available as definition extractors:
- `bert-base-cased` can be used to extract definitional contexts from English Wikipedia articles
- `bert-base-multilingual-cased` can be used to extract definitional contexts from Italian Wikipedia articles (or other languages)

##### How-To Guide

The BERT models need to be trained on a manually annotated dataset. We trained them on [this manually annotated dataset](http://lcl.uniroma1.it/wcl/) made of Wikipedia sentences. The dataset was divided into 80% for the training, 10& for testing and 10% for validation. The code for the training is in folder `defXlink/BERT/bert_training`

The folder `defXlink/BERT/definition_extractor/` contains four files:
- `defextr_first2sentences_EN.py` extracts the first two sentences with a positive score above the threshold of 0.6 from an English Wikipedia article
- `defextr_first2sentences_IT.py` extracts the first two sentences with a positive score above the threshold of 0.6 from an Italian Wikipedia article (it can be used with any other language)
- `defextr_top_score_EN.py` extracts the sentence with the highest score overall in the English Wikipedia article
- `defextr_top_score_IT.py` extracts the sentence with the highest score overall in the Italian Wikipedia article

For both cases (top score and first 2 sentences), the implementation is the same:
- You will be prompted to give the path where the Wikipedia article is stored with `path_to_text = input("Enter the path to the text:\n")`
- The Wikipedia article has to be sentencized, i.e. tokenized in sentences. We use `SpaCy` for the English articles and `sentence_splitter` for Italian articles
-  
