import spacy
import textacy
#import urllib.request
import re
# https://pypi.org/project/Wikipedia-API/
import wikipediaapi as wa
from spacy.tokens import Doc

def preprocessing(doc):
    nlp = spacy.load("it_core_news_lg")
    doc = nlp(sentence)
    tok_list = []
    for tok in doc:
        if tok.text == "d'":
            tok = tok.lemma_
        else:
            tok = tok.text
        tok_list.append(tok)
        merge = list(nlp.pipe(tok_list))
        doc = Doc.from_docs(merge)
    return doc

def get_candidates(doc):
    #candidates = []
    extracted = list(textacy.extract.ngrams(doc, n, filter_stops = False))
    #candidates.extend(extracted)
    return extracted

sentence = "negli spaghetti alle vongole ci sta bene l'olio d'oliva"

    
doc = preprocessing(sentence)
clean_ngrams = []
for n in range(4, 0, -1):
    candidates = get_candidates(doc)
    print(candidates)
    for ngram in candidates:   
        if not any([ngram in other_ngram for other_ngram in sorting]):
            sorting.append(ngram)
    
       
