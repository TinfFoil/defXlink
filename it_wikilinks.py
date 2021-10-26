import xml.sax
import subprocess
import mwparserfromhell
import re
import os

path = '/home/mmartinelli/persistent/it_wikilinks'
data_path = r"/home/mmartinelli/project/corpora/wikidumps/itwiki-20210720-pages-articles-multistream.xml.bz2"

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
        self._categories = ["Categoria:Antipasti", "Categoria:Contorni", "Categoria:Dolci", 
              "Categoria:Piatti", "Categoria:Primi piatti", "Categoria:Secondi piatti"]

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
            self.dish_parser(self._values['title'], self._values['id'], self._values['text'])
            #self._pages.append((self._values['title'], self._values['id'], self._values['text']))
            #print(self._pages[-1])
            
    def dish_parser(self, title, myid, text):
        texts = []
        if any(cat in text for cat in self._categories):
            texts.append(text)
            #titles = [x[0] for x in texts]
            parsed = mwparserfromhell.parse(text)        
            """
            dishes = x.strip_code().strip()
            wikified_dishes.append(texts)
            dishes = re.sub(r"(== Note == | ==Note== )\n *(.)*", "", dishes, flags=re.DOTALL)
            dishes = re.sub(r"<[^>]+>", "", dishes)
            dishes = re.sub(r"(  )*", "", dishes)
            dishes = "\n".join([title, parsed])
            #dishes = "\n".join(x) for x in zip(titles, dishes)]
            """
            wikilinks = parsed.filter_wikilinks()
            #print(type(wikilinks))
            wikilinks = [str(link) for link in wikilinks]
            wikilinks = [re.sub(r"(\[\[)(.*)(\]\])", r"\2", link) for link in wikilinks]
            wikilinks = [link for link in wikilinks if "File" not in link]
            wikilinks = [link for link in wikilinks if "Categoria" not in link]
            wikilinks = [link for link in wikilinks if not link.isdigit()]
            wikilinks = [''.join(x for x in link if not x.isdigit()) for link in wikilinks]
            #print(wikilinks)
            
            ids = myid
            content = wikilinks
            file = '{}.txt'.format(ids)
            with open(os.path.join(path, file), 'w') as f:
                f.write('{}'.format(content))
            
    
# Object for handling xml
handler = WikiXmlHandler()

# Parsing object
parser = xml.sax.make_parser()
parser.setContentHandler(handler)


counter = 0

# Iterating through compressed file
for i, line in enumerate(subprocess.Popen(['bzcat'], stdin = open(data_path), stdout = subprocess.PIPE).stdout):
    
    parser.feed(line)
    
    if len(handler._pages) > 70000:
        break
#    counter += 1
#    if counter % 100000 == 0:
#        print("Current loop:", counter)