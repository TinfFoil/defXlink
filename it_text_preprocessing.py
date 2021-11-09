import spacy
import textacy
import urllib.request
import re
# https://pypi.org/project/Wikipedia-API/
import wikipediaapi as wa
from spacy.tokens import Doc

def preprocessing(text):
    """invoke spacy IT model and pass the text in the model
    return spacy doc"""
    nlp = spacy.load("it_core_news_lg")
    doc = nlp(sentence)
    return doc

def get_candidates(doc):
    """create ngrams with textacy
    return list of candidate ngrams"""
    candidates = []
    extracted = list(textacy.extract.ngrams(doc, n, filter_stops = False))
    candidates.extend(extracted)
    return candidates

def get_substring(string_list):
    """sort ngrams from longest to shortest
    delete shorter ngrams present in the longest ones
    return list of ngrams as textacy objects"""
    string_list.sort(key=lambda ngram: len(ngram), reverse=True)
    out = []
    for ngram in string_list:
        if not any([ngram in other_ngram for other_ngram in out]):
            out.append(ngram)
    return out

def get_wikipedia_url(ngrams_list):
    """invoke wikipedia API
    turn ngrams into strings
    check if ngram exist as IT wikipedia page and remove disambiguation pages
    clean tokens
    invoke get_substring
    return url"""
    # CONSTANTS
    language = "it"
    # INVOCATION
    it_wiki = wa.Wikipedia(language)
    clean_ngrams = []
    for tok in candidates:
        page = it_wiki.page(str(tok))
        if page.exists() and "Categoria:Pagine di disambiguazione" not in page.categories:
            #if "Categoria:Pagine di disambiguazione" not in page.categories:
            clean_ngrams.append(re.sub(r" \(id.*\)", "", str(page)))
            sorted_ngrams = get_substring(clean_ngrams)
            url_list = [f"https://it.wikipedia.org/wiki/{str(tok.replace(' ', '_'))}" for tok in sorted_ngrams]
        else:
            pass
    return url_list

# example sentence
sentence = """Per preparare gli spaghetti alle vongole, cominciate dalla pulizia. 
Assicuratevi che non ci siano gusci rotti o vuoti, andranno scartati.
Trascorso il tempo le vongole avranno spurgato eventuali residui di sabbia. In un tegame mettete a scaldare un po' d'olio d'oliva[4]. 
Poi aggiungete uno spicchio d'aglio e, metre questo si insaporisce, scolate bene le, 
sciacquatele e tuffatele nel tegame caldo [5]. Chudete con il coperchio e lasciate cuocere per qualche minuto a fiamma alta [6].
Le vongole si apriranno con il calore, quindi agitate di tanto in tanto il tegame 
finché non si saranno completamente dischiuse [7]. 
A fine cottura unite anche le vongole ed il prezzemolo tritato [11]!"""

doc = preprocessing(sentence)

for n in range(4, 0, -1):
    candidates = get_candidates(doc)
    
url_list = get_wikipedia_url(candidates) 

print(len(url_list))

print(url_list)
