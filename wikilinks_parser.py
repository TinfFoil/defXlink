import xml.sax
import subprocess
import mwparserfromhell
import re
import os

data_path = r"/home/mmartinelli/project/corpora/wikidumps/itwiki-20210720-pages-articles-multistream.xml.bz2"
path = '/home/jupyter-margherita/corpora/wiki-it-food-idk'

# Function where ContentHandler looks for opening and closing tags title and text 
# and adds characters enclosed within them to the buffer
# content saved to a dict with tag as key

class WikiXmlHandler(xml.sax.handler.ContentHandler):
    """Content handler for Wiki XML data using SAX"""
    def __init__(self):
        xml.sax.handler.ContentHandler.__init__(self)
        self._buffer = None
        self._values = {}
        self._current_tag = None
        self._pages = []
        self._counter = 0
        self._flag = True

    def characters(self, content):
        """Characters between opening and closing tags"""
        if self._current_tag:
            self._buffer.append(content)

    def startElement(self, name, attrs):
        """Opening tag of element"""
        if name in ('title', 'id', 'text', 'timestamp'):         #do we need timestamp?
            self._current_tag = name
            self._buffer = []

    def endElement(self, name):
        """Closing tag of element"""
        if name == self._current_tag:
            #print(name, self._buffer)
            if self._current_tag == "id": 
                if self._flag:
                    self._values[name] = ' '.join(self._buffer)
                    self._flag = False
            else:
                self._values[name] = ' '.join(self._buffer)

        if name == 'page':
            self._flag = True
            self._pages.append((self._values['title'], self._values['id'], self._values['text']))
            #print(self._pages[-1])


# Object for handling xml
handler = WikiXmlHandler()

# Parsing object
parser = xml.sax.make_parser()
parser.setContentHandler(handler)

#lst = []

counter = 0

# Iterating through compressed file
for i, line in enumerate(subprocess.Popen(['bzcat'], stdin = open(data_path), stdout = subprocess.PIPE).stdout):
    
    parser.feed(line)
    
    if len(handler._pages) > 70000:
        break
    #counter += 1
    #if counter % 10000 == 0:
    #    print("Current loop:", counter)

# Append all articles that have the strings defined in categories in wikified_dishes list 
# the list has tuples with [0] being the title and [1] being the text
# get [[wikilinks]]

wikified_dishes = []
categories = ["Categoria:Antipasti", "Categoria:Contorni", "Categoria:Dolci", 
              "Categoria:Piatti", "Categoria:Primi piatti", "Categoria:Secondi piatti"]

texts = []

for x in handler._pages:
    if any(cat in x[2] for cat in categories):
        texts.append(x)
        titles = [x[0] for x in texts]
        dishes = [mwparserfromhell.parse(x[2]) for x in texts]
        wikilinks = [links.filter_wikilinks() for links in dishes]
        # extract links from inside list of links and turn them in str objects
        wikilinks = [str(link) for linklist in wikilinks for link in linklist]
        # clean list from [[]] and unwanted substrings like "File" and "Categoria"
        wikilinks = [re.sub(r"(\[\[)(.*)(\]\])", r"\2", link) for link in wikilinks]
        wikilinks = [link for link in wikilinks if "File" not in link]
        wikilinks = [link for link in wikilinks if "Categoria" not in link]
        wikilinks = [link for link in wikilinks if not link.isdigit()]
        wikilinks = [''.join(x for x in i if not x.isdigit()) for i in wikilinks]

        #remove duplicates
        wikilinks = list(dict.fromkeys(wikilinks))
    else:
        pass

print(len(wikilinks))
print(len(titles))
print(len(dishes))
#print(wikilinks)



