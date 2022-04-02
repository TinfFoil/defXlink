# defXlink

defXlink is a project that branches into two objectives:
- Automatic definitional context extraction for Wikipedia articles;
- Automatic definitions linking for food recipes.

⚠️ We've worked with Italian and English, so basically every code is doubled. I suggest you refer to the English one.

## Premises: Build your Own Wikipedia Corpus

In order to use the BERT models as definition extractors, you first need a tailor-made corpus, possibly from Wikipedia (or not really, it's your call).
The folder `corpora` contains four Python files. `wiki_parser_EN.py` is the code to parse the English dump of Wikipedia to extract food-related Wikipedia articles. 
Some lines of code that may turn out useful:
- 📂 `path`: the path where you want to save your ad-hoc corpus;
- 📂 `data_path`: the path where the Wikipedia dump is stored;
- `self._categories`: Wikipedia articles are connected through the categories in the category tree. If you want a corpus on food, you look for food categories, if you want a corpus on animals, you look for animal categories, and so on. ⚠️ If you don't need the categories and want to parse the entire dump, comment this line 24 as well as line 67;
- 📝 `parsed`: lines 71-74 use the library `mwparserfromhell` to clean the XML file by turning it into a string and removing the unnecessary information with regex. ⚠️ If you want to keep the entire article, comment these lines.

## Definitional Context Extraction

Two trained BERT models are available as definition extractors:
- `bert-base-cased` can be used to extract definitional contexts from English Wikipedia articles;
- `bert-base-multilingual-cased` can be used to extract definitional contexts from Italian Wikipedia articles (or other languages)

##### How-To Guide

The BERT models need to be trained on a manually annotated dataset. We trained them on [this manually annotated dataset](http://lcl.uniroma1.it/wcl/) made of Wikipedia sentences. The dataset was divided into 80% for the training, 10& for testing and 10% for validation. The code for the training is in folder `defXlink/BERT/bert_training`.

The folder `defXlink/BERT/definition_extractor/` contains four files:
- `defextr_first2sentences_EN.py` extracts the first two sentences with a positive score above the threshold of 0.6 from an English Wikipedia article;
- `defextr_first2sentences_IT.py` extracts the first two sentences with a positive score above the threshold of 0.6 from an Italian Wikipedia article (it can be used with any other language);
- `defextr_top_score_EN.py` extracts the sentence with the highest score overall in the English Wikipedia article;
- `defextr_top_score_IT.py` extracts the sentence with the highest score overall in the Italian Wikipedia article.

For both cases (top score and first 2 sentences), the implementation is the same:
- 📂 `path_to_text = input("Enter the path to the text:\n")`: prompts you to give the path where the Wikipedia article is stored;
- The Wikipedia article has to be sentencized, i.e. tokenized in sentences. We use `SpaCy` for the English articles and `sentence_splitter` for Italian articles;
- Let the model do the work for you. If you are curious, most of the code is freely available on [the Huggingface website](https://huggingface.co/course/chapter3/3?fw=pt);
- ✏️ You can modify the final lines of the code according to the output you wish to get from the model.
