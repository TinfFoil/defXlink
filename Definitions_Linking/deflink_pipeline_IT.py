import spacy
import textacy
import re
import wikipediaapi as wa
from spacy.tokens import Doc

# Create set of wiki titles

from pathlib import Path
path = Path("/home/jupyter-margherita/corpora/wiki-it-food/")

set_itwiki = set()
for doc in path.iterdir():
    #print(doc)
    if doc.is_file():
        with open(doc) as f:
            mydoc = f.readline()
            mydoc = mydoc.replace("\n", "")
            set_itwiki.add(mydoc.casefold())
#print(len(set_itwiki))
#print(set_itwiki)

def preprocessing(doc):
    """
    invoke spacy IT model and pass the text in the model
    lemmatize only token d' into di
    import stopwords
    turn list of strings into one spacy doc
    return spacy doc
    """
    nlp = spacy.load("it_core_news_lg")
    stop1 = nlp.Defaults.stop_words
    stop2 = {"a","abbastanza","abbia","abbiamo","abbiano","abbiate","accidenti","ad","adesso","affinché","agl","agli","ahime","ahimè","ai","al","alcuna","alcuni","alcuno","all","alla","alle","allo","allora","altre","altri","altrimenti","altro","altrove","altrui","anche","ancora","anni","anno","ansa","anticipo","assai","attesa","attraverso","avanti","avemmo","avendo","avente","aver","avere","averlo","avesse","avessero","avessi","avessimo","aveste","avesti","avete","aveva","avevamo","avevano","avevate","avevi","avevo","avrai","avranno","avrebbe","avrebbero","avrei","avremmo","avremo","avreste","avresti","avrete","avrà","avrò","avuta","avute","avuti","avuto","basta","ben","bene","benissimo","brava","bravo","buono","c","caso","cento","certa","certe","certi","certo","che","chi","chicchessia","chiunque","ci","ciascuna","ciascuno","cima","cinque","cio","cioe","cioè","circa","citta","città","ciò","co","codesta","codesti","codesto","cogli","coi","col","colei","coll","coloro","colui","come","cominci","comprare","comunque","con","concernente","conclusione","consecutivi","consecutivo","consiglio","contro","cortesia","cos","cosa","cosi","così","cui","d","da","dagl","dagli","dai","dal","dall","dalla","dalle","dallo","dappertutto","davanti","degl","degli","dei","del","dell","della","delle","dello","dentro","detto","deve","devo","di","dice","dietro","dire","dirimpetto","diventa","diventare","diventato","dopo","doppio","dov","dove","dovra","dovrà","dovunque","due","dunque","durante","e","ebbe","ebbero","ebbi","ecc","ecco","ed","effettivamente","egli","ella","entrambi","eppure","era","erano","eravamo","eravate","eri","ero","esempio","esse","essendo","esser","essere","essi","ex","fa","faccia","facciamo","facciano","facciate","faccio","facemmo","facendo","facesse","facessero","facessi","facessimo","faceste","facesti","faceva","facevamo","facevano","facevate","facevi","facevo","fai","fanno","farai","faranno","fare","farebbe","farebbero","farei","faremmo","faremo","fareste","faresti","farete","farà","farò","fatto","favore","fece","fecero","feci","fin","finalmente","finche","fine","fino","forse","forza","fosse","fossero","fossi","fossimo","foste","fosti","fra","frattempo","fu","fui","fummo","fuori","furono","futuro","generale","gente","gia","giacche","giorni","giorno","giu","già","gli","gliela","gliele","glieli","glielo","gliene","grande","grazie","gruppo","ha","haha","hai","hanno","ho","i","ie","ieri","il","improvviso","in","inc","indietro","infatti","inoltre","insieme","intanto","intorno","invece","io","l","la","lasciato","lato","le","lei","li","lo","lontano","loro","lui","lungo","luogo","là","ma","macche","magari","maggior","mai","male","malgrado","malissimo","me","medesimo","mediante","meglio","meno","mentre","mesi","mezzo","mi","mia","mie","miei","mila","miliardi","milioni","minimi","mio","modo","molta","molti","moltissimo","molto","momento","mondo","ne","negl","negli","nei","nel","nell","nella","nelle","nello","nemmeno","neppure","nessun","nessuna","nessuno","niente","no","noi","nome","non","nondimeno","nonostante","nonsia","nostra","nostre","nostri","nostro","novanta","nove","nulla","nuovi","nuovo","o","od","oggi","ogni","ognuna","ognuno","oltre","oppure","ora","ore","osi","ossia","ottanta","otto","paese","parecchi","parecchie","parecchio","parte","partendo","peccato","peggio","per","perche","perchè","perché","percio","perciò","perfino","pero","persino","persone","però","piedi","pieno","piglia","piu","piuttosto","più","po","pochissimo","poco","poi","poiche","possa","possedere","posteriore","posto","potrebbe","preferibilmente","presa","press","prima","primo","principalmente","probabilmente","promesso","proprio","puo","pure","purtroppo","può","qua","qualche","qualcosa","qualcuna","qualcuno","quale","quali","qualunque","quando","quanta","quante","quanti","quanto","quantunque","quarto","quasi","quattro","quel","quella","quelle","quelli","quello","quest","questa","queste","questi","questo","qui","quindi","quinto","realmente","recente","recentemente","registrazione","relativo","riecco","rispetto","salvo","sara","sarai","sa
    stopwords = stop1.union(stop2)
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
    return doc, stopwords

def get_candidates(doc, n):
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
    ngram_list.sort(key=lambda ngram: len(ngram), reverse=True)
    sorted_ngrams = []
    for ngram in ngram_list:
        if not any([ngram in other_ngram for other_ngram in sorted_ngrams]):
            sorted_ngrams.append(ngram)
    return sorted_ngrams

sentence = "fiori di zucca in pastella"
# CONSTANTS
language = "it"
# INVOCATION
it_wiki = wa.Wikipedia(language)

doc, stopwords = preprocessing(sentence)

clean_ngrams = []
string_page = {}

for n in range(4, 0, -1):
    candidates = get_candidates(doc, n)
    for tok in candidates:
        # Ignore stopwords and digits
        if any([str(tok).casefold()==stopword for stopword in stopwords]):
            continue
        if str(tok).isdigit():
            continue
        # Query Wikipedia API to find if page exists and is not a pagina di disambiguazione
        # Clean Wikipedia API object
        # Append to dict
        page = it_wiki.page(str(tok))
        if page.exists() and "Categoria:Pagine di disambiguazione" not in page.categories:
            cleaned_page = re.sub(r" \(id.*\)", "", str(page).casefold())
            clean_ngrams.append(cleaned_page)
            string_page[cleaned_page] = str(tok)
            

sorted_ngrams = get_substring(clean_ngrams)
final_dict = {}
cleaned_final_dict = {}

cleaned_values = get_substring(list(string_page.values()))

for key in string_page:
    if any([string_page[key]==clean for clean in cleaned_values]):
        final_dict[key] = string_page[key]
        
for key in final_dict:
    if any([key==ngram for ngram in sorted_ngrams]):
        cleaned_final_dict[key] = final_dict[key]

# dict with string (aka mention) as key and url as value
url_dict = {final_dict[found]:f"https://it.wikipedia.org/wiki/{str(found.replace(' ', '_'))}" for found in cleaned_final_dict}

print(url_dict)

text = "Fiori di zucca in pastella"
# Preprocessing
text, stopwords = preprocessing(text)
tokens = []
for n in text:
    tokens.append(n.text)

# HTML version with href tags
tokens = ' '.join(tokens)
print(list(url_dict.keys()))
for key in url_dict:
    # Remove space if dealing with titles
    if f" {key}" in f" {tokens}":
        tokens = f" {tokens}".replace(f" {key}",f' <a href="{url_dict[key]}">{key}</a>')
# Remove whitespace before punctuation marks
html = re.sub(r" (\.|\;|\,|\:|\!|\?|\)|\]|\}|\')", r'\1', tokens)
print(html)

# food or other class
# Iterate over keys in dict and look for exact string match of the key inside the set of all wiki titles
for key in cleaned_final_dict.keys():
    if any([key == title for title in set_itwiki]):
        html = html.replace(f' <a href="{url_dict[cleaned_final_dict[key]]}">{cleaned_final_dict[key]}</a>', f' <a class="food" href="{url_dict[cleaned_final_dict[key]]}">{cleaned_final_dict[key]}</a>')
    else:
        html = html.replace(f' <a href="{url_dict[cleaned_final_dict[key]]}">{cleaned_final_dict[key]}</a>', f' <a class="other" href="{url_dict[cleaned_final_dict[key]]}">{cleaned_final_dict[key]}</a>')

print(html)
