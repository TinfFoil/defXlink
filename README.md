# defXlink

defXlink is a project that branches into two objectives:
- Automatic definitional context extraction for Wikipedia articles
- Automatic definitions linking for food recipes

These involve the Italian and English languages.

## Definitional Context Extraction

Two trained BERT models are available as definition extractors:
- `bert-base-cased` can be used to extract definitional contexts from English Wikipedia articles
- `bert-base-multilingual-cased` can be used to extract definitional contexts from Italian Wikipedia articles (or other languages)

##### How-To Guide

The BERT models need to be trained on a manually annotated dataset. We trained them on a dataset available here

The folder `defXlink/BERT/definition_extractor/` contains four files:
- `defextr_first2sentences_EN.py` extracts the first two sentences with a positive score above the threshold of 0.6 from an English Wikipedia article
- `defextr_first2sentences_IT.py` extracts the first two sentences with a positive score above the threshold of 0.6 from an Italian Wikipedia article (it can be used with any other language)
- `defextr_top_score_EN.py` extracts the sentence with the highest score overall in the English Wikipedia article
- `defextr_top_score_IT.py` extracts the sentence with the highest score overall in the Italian Wikipedia article

For both cases (top score and first 2 sentences), the implementation is the same:
- You will be prompted to give the path where the Wikipedia article is stored with `path_to_text = input("Enter the path to the text:\n")`
- The Wikipedia article has to be sentencized, i.e. tokenized in sentences. We use `SpaCy` for the English articles and `sentence_splitter` for Italian articles
-  
