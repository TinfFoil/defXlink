import spacy
import textacy
import re
# https://pypi.org/project/Wikipedia-API/
import wikipediaapi as wa
from spacy.tokens import Doc

def preprocessing(doc):
    """
    invoke spacy IT model and pass the text in the model
    lemmatize only token d' into di
    turn list of strings into one spacy doc
    return spacy doc
    """
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
    """
    create ngrams with textacy keeping also stopwords
    return list of candidate ngrams
    """
    extracted = list(textacy.extract.ngrams(doc, n, filter_stops = False))
    return extracted

def get_substring(ngram_list):
    """
    delete shorter ngrams present in the longer ones
    return list of ngrams as textacy objects
    """
    sorted_ngrams = []
    for ngram in ngram_list:
        if not any([ngram in other_ngram for other_ngram in sorted_ngrams]):
            sorted_ngrams.append(ngram)
    return sorted_ngrams

sentence = """Per preparare gli spaghetti alle vongole, cominciate dalla pulizia. 
Assicuratevi che non ci siano gusci rotti o vuoti, andranno scartati.
Trascorso il tempo le vongole avranno spurgato eventuali residui di sabbia. In un tegame mettete a scaldare un po' d'olio d'oliva[4]. 
Poi aggiungete uno spicchio d'aglio e, metre questo si insaporisce, scolate bene le, 
sciacquatele e tuffatele nel tegame caldo [5]. Chudete con il coperchio e lasciate cuocere per qualche minuto a fiamma alta [6].
Le vongole si apriranno con il calore, quindi agitate di tanto in tanto il tegame 
finché non si saranno completamente dischiuse [7]. 
A fine cottura unite anche le vongole ed il prezzemolo tritato [11]!"""

# CONSTANTS
language = "it"
# INVOCATION
it_wiki = wa.Wikipedia(language)

doc = preprocessing(sentence)

clean_ngrams = []
url_list = []
for n in range(4, 0, -1):
    candidates = get_candidates(doc)
    #print(candidates)
    for tok in candidates:
        page = it_wiki.page(str(tok))
        if page.exists() and "Categoria:Pagine di disambiguazione" not in page.categories:
            clean_ngrams.append(re.sub(r" \(id.*\)", "", str(page).lower()))
            #print(clean_ngrams)
            sorted_ngrams = get_substring(clean_ngrams)
            url_list = [f"https://it.wikipedia.org/wiki/{str(tok.replace(' ', '_'))}" for tok in sorted_ngrams]
print(url_list)
