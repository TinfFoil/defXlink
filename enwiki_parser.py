import xml.sax
import subprocess
import mwparserfromhell
import re
import os

path = '/home/mmartinelli/persistent/en-wiki-food'
data_path = r"/home/mmartinelli/project/corpora/wikidumps/enwiki-20210720-pages-articles-multistream.xml.bz2"

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
        self._categories = ["Category:Italian cuisine", "Category:Cuisine of Abruzzo", 
              "Category:Cuisine of Apulia", "Category:Cuisine of Basilicata", "Category:Cuisine of Calabria",
              "Category:Cuisine of Campania", "Category:Cuisine of Emilia-Romagna", "Category:Cuisine of Lazio", 
              "Category:Cuisine of Liguria", "Category:Cuisine of Lombardy", "Category:Cuisine of Marche",
              "Category:Cuisine of Molise", "Category:Cuisine of Piedmond", "Category:Cuisine of Sardinia",
              "Category:Cuisine of Sicily", "Category:Cuisine of South Tyrol", "Category:Cuisine of Tuscany",
              "Category:Cuisine of Umbria", "Category:Cuisine of Veneto",
              "Category:Cuisine of Aosta Valley", "Category:Dairy dishes", "Category:Egg dishes", 
              "Category:Flower dishes", "Category:Fruit dishes", "Category:Ginger dishes", "Category:Grain dishes", 
              "Category:Meat dishes", "Category:Mushroom dishes", "Category:Noodle dishes", "Category:Nut dishes", 
              "Category:Pasta dishes", "Category:Tofu dishes", "Category:Tuber dishes", "Category:Vegetable dishes", "Category:Spaghetti dishes",
              "Category:Neapolitan cuisine", "Category:Potato dishes", "Category:Fish dishes", "Category:Italian desserts",
              "Category:Appetizers", "Category:Desserts"]

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
            parsed = mwparserfromhell.parse(text).strip_code().strip()         
            parsed = re.sub(r"(== See also == | ==See also== )\n *(.)*", "", parsed, flags=re.DOTALL)
            parsed = re.sub(r"<[^>]+>", "", parsed)
            parsed = re.sub(r"(  )*", "", parsed)
            parsed = "\n".join([title, parsed])
            #parsed = ["\n".join(x) for x in zip(titles, parsed)]
            
            ids = myid
            article = parsed
            file = '{}.txt'.format(ids)
            with open(os.path.join(path, file), 'w') as f:
                f.write('{}'.format(article))

    
# Object for handling xml
handler = WikiXmlHandler()

# Parsing object
parser = xml.sax.make_parser()
parser.setContentHandler(handler)


counter = 0

# Iterating through compressed file
for i, line in enumerate(subprocess.Popen(['bzcat'], stdin = open(data_path), stdout = subprocess.PIPE).stdout):
    
    parser.feed(line)
    
#    if len(handler._pages) > 70000:
#        break
    counter += 1
    if counter % 100000 == 0:
        print("Current loop:", counter)
