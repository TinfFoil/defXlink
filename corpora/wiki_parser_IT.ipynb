{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 71,
   "id": "24a56a77",
   "metadata": {},
   "outputs": [],
   "source": [
    "import xml.sax\n",
    "import subprocess\n",
    "import mwparserfromhell\n",
    "import re\n",
    "import os"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 72,
   "id": "26f8f12a",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Function where ContentHandler looks for opening and closing tags title and text \n",
    "# and adds characters enclosed within them to the buffer\n",
    "# content saved to a dict with tag as key\n",
    "\n",
    "class WikiXmlHandler(xml.sax.handler.ContentHandler):\n",
    "    \"\"\"Content handler for Wiki XML data using SAX\"\"\"\n",
    "    def __init__(self):\n",
    "        xml.sax.handler.ContentHandler.__init__(self)\n",
    "        self._buffer = None\n",
    "        self._values = {}\n",
    "        self._current_tag = None\n",
    "        self._pages = []\n",
    "        self._counter = 0\n",
    "        self._flag = True\n",
    "\n",
    "    def characters(self, content):\n",
    "        \"\"\"Characters between opening and closing tags\"\"\"\n",
    "        if self._current_tag:\n",
    "            self._buffer.append(content)\n",
    "\n",
    "    def startElement(self, name, attrs):\n",
    "        \"\"\"Opening tag of element\"\"\"\n",
    "        if name in ('title', 'id', 'text', 'timestamp'):         #do we need timestamp?\n",
    "            self._current_tag = name\n",
    "            self._buffer = []\n",
    "\n",
    "    def endElement(self, name):\n",
    "        \"\"\"Closing tag of element\"\"\"\n",
    "        if name == self._current_tag:\n",
    "            #print(name, self._buffer)\n",
    "            if self._current_tag == \"id\": \n",
    "                if self._flag:\n",
    "                    self._values[name] = ' '.join(self._buffer)\n",
    "                    self._flag = False\n",
    "            else:\n",
    "                self._values[name] = ' '.join(self._buffer)\n",
    "\n",
    "        if name == 'page':\n",
    "            self._flag = True\n",
    "            self._pages.append((self._values['title'], self._values['id'], self._values['text']))\n",
    "            #print(self._pages[-1])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 73,
   "id": "ced7a7f2",
   "metadata": {},
   "outputs": [],
   "source": [
    "data_path = r\"/home/mmartinelli/project/corpora/wikidumps/itwiki-20210720-pages-articles-multistream.xml.bz2\"\n",
    "# Object for handling xml\n",
    "handler = WikiXmlHandler()\n",
    "\n",
    "# Parsing object\n",
    "parser = xml.sax.make_parser()\n",
    "parser.setContentHandler(handler)\n",
    "\n",
    "#lst = []\n",
    "\n",
    "counter = 0\n",
    "\n",
    "# Iterating through compressed file\n",
    "for i, line in enumerate(subprocess.Popen(['bzcat'], stdin = open(data_path), stdout = subprocess.PIPE).stdout):\n",
    "    \n",
    "    parser.feed(line)\n",
    "    \n",
    "    #if len(handler._pages) > 70000:\n",
    "    #    break\n",
    "    counter += 1\n",
    "    if counter % 10000 == 0:\n",
    "        print(\"Current loop:\", counter)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 74,
   "id": "a04689c6",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "49\n"
     ]
    }
   ],
   "source": [
    "# Append all articles that have the strings defined in categories in wikified_dishes list \n",
    "# the list has tuples with [0] being the title and [1] being the text\n",
    "\n",
    "wikified_dishes = []\n",
    "categories = [\"Categoria:Antipasti\", \"Categoria:Contorni\", \"Categoria:Dolci\", \n",
    "              \"Categoria:Piatti\", \"Categoria:Primi piatti\", \"Categoria:Secondi piatti\"]\n",
    "\n",
    "#categories = [\"Categoria:Cucina per tipo di pietanze\"]\n",
    "for x in handler._pages:\n",
    "    if any(cat in x[2] for cat in categories):\n",
    "        wikified_dishes.append(x)\n",
    "    else:\n",
    "        pass\n",
    "print(len(wikified_dishes))\n",
    "#print(wikified_dishes[26])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 75,
   "id": "bf595e2b",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Create title list and append only titles (element 0 of tuples in wikified_dishes)\n",
    "\n",
    "title_lst = [el[0] for el in wikified_dishes]\n",
    "\n",
    "# Create id list and append only ids (el 1 of tuples in wikified_dishes)\n",
    "\n",
    "id_lst = [el[1] for el in wikified_dishes]\n",
    "\n",
    "# Create text list and append only texts (element 2 of tuples in wikified_dishes)\n",
    "\n",
    "text_lst = [el[2] for el in wikified_dishes]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 76,
   "id": "9a86933c",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Parse text list\n",
    "\n",
    "text_lst = [mwparserfromhell.parse(text) for text in text_lst]\n",
    "\n",
    "# Clean texts\n",
    "\n",
    "text_lst = [text.strip_code().strip() for text in text_lst]\n",
    "\n",
    "# Clean texts from 'Note' until the end and other undeleted tags with regex\n",
    "\n",
    "clean_text_lst = [re.sub(r\"(== Note == | ==Note== )\\n *(.)*\", \"\", el, flags=re.DOTALL) for el in text_lst]\n",
    "clean_text_lst = [re.sub(r\"( < ref > | < /ref > )\", \"\", el) for el in clean_text_lst]\n",
    "clean_text_lst = [re.sub(r\"<[^>]+>\", \"\", el) for el in clean_text_lst]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 77,
   "id": "9719f1c5",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Join title and text\n",
    "\n",
    "wiki = ['\\n'.join(x) for x in zip(title_lst, clean_text_lst)]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 78,
   "id": "f57dffbc",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Write texts in txt files with id as title\n",
    "\n",
    "path = '/home/jupyter-margherita/corpora/wiki-it-food'\n",
    "\n",
    "for el, article in zip(wikified_dishes, wiki):\n",
    "    ids = el[1]\n",
    "    article = article\n",
    "    file = f'{ids}.txt'\n",
    "    if not any(ban in el[0] for ban in [\"/\", \"Categoria:\"]): \n",
    "        with open(os.path.join(path, file), 'w+') as f:\n",
    "            f.write(f'{article}')\n",
    "\n",
    "#print(os.listdir(path))\n"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.7.11"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
