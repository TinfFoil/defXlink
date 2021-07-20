from bs4 import BeautifulSoup
import requests
import re

# create dict with sections:n-pages as key:value pairs, iterate over them as
# many times as the value and append each page with the links to the dishes to pages_lst

# sections = {"https://www.giallozafferano.it/ricette-cat/": 383,
#             "https://www.giallozafferano.it/ricette-cat/Antipasti/": 75,
#             "https://www.giallozafferano.it/ricette-cat/Primi/": 86,
#             "https://www.giallozafferano.it/ricette-cat/Secondi-piatti/": 66,
#             "https://www.giallozafferano.it/ricette-cat/Contorni/": 19,
#             "https://www.giallozafferano.it/ricette-cat/Dolci-e-Desserts/": 118,
#             "https://www.giallozafferano.it/ricette-cat/Lievitati/": 25,
#             "https://www.giallozafferano.it/ricette-cat/Piatti-Unici/": 30,
#             "https://www.giallozafferano.it/ricette-cat/facili-e-veloci/": 74,
#             "https://www.giallozafferano.it/ricette-cat/Primi/pasta/": 42,
#             "https://www.giallozafferano.it/ricette-cat/Antipasti/facili-e-veloci/": 19,
#             "https://www.giallozafferano.it/ricette-cat/Lievitati/Pizze-e-focacce/": 10,
#             "https://www.giallozafferano.it/ricette-cat/Lievitati/pane/": 9,
#             "https://www.giallozafferano.it/ricette-cat/Finger-food/": 45,
#             "https://www.giallozafferano.it/ricette-cat/Torte-salate/": 11,
#             "https://www.giallozafferano.it/ricette-cat/Al-forno/": 141,
#             "https://www.giallozafferano.it/ricette-cat/Insalate/": 6,
#             "https://www.giallozafferano.it/ricette-cat/Primi/Pasta-fresca/": 14,
#             "https://www.giallozafferano.it/ricette-cat/Primi/facili-e-veloci/": 20,
#             "https://www.giallozafferano.it/ricette-cat/Primi/pasta/grandi-classici/": 7,
#             "https://www.giallozafferano.it/ricette-cat/Primi/pasta/Sfiziosi/": 30,
#             "https://www.giallozafferano.it/ricette-cat/Primi/Gnocchi/": 7,
#             "https://www.giallozafferano.it/ricette-cat/Primi/riso-cereali/": 16,
#             "https://www.giallozafferano.it/ricette-cat/Secondi-piatti/Pesce/": 22,
#             "https://www.giallozafferano.it/ricette-cat/Secondi-piatti/Vegetariani/": 12,
#             "https://www.giallozafferano.it/ricette-cat/Dolci-e-Desserts/Biscotti/": 13,
#             "https://www.giallozafferano.it/ricette-cat/Dolci-e-Desserts/piccola-pasticceria/": 37,
#             "https://www.giallozafferano.it/ricette-cat/Dolci-e-Desserts/facili-e-veloci/": 18,
#             "https://www.giallozafferano.it/ricette-cat/Dolci-e-Desserts/Torte/": 43,
#             "https://www.giallozafferano.it/ricette-cat/al-cioccolato/": 30,
#             "https://www.giallozafferano.it/ricette-cat/Dolci-e-Desserts/Torte/facili-e-veloci/": 5,
#             "https://www.giallozafferano.it/ricette-cat/Marmellate-e-Conserve/Marmellate/": 4,
#             "https://www.giallozafferano.it/ricette-cat/Carne/": 43,
#             "https://www.giallozafferano.it/ricette-cat/Pesce/": 55,
#             "https://www.giallozafferano.it/ricette-cat/Vegetariani/": 203
#         }

sections = {"https://www.giallozafferano.it/ricette-cat/": 2}

pages_lst = []
for section in sections:
    for i in range(1, sections[section]):
      page = "".join([section, "page", str(i)])
      pages_lst.append(page)
# print(pages_lst)
print("Number of section URLs produced:",  len(pages_lst))


# for each page, get the section enclosed in the tag h2, class and in that get a, href and append it to dishes_lst
dishes_lst = []
for url in pages_lst:
    get_url = requests.get(url)
    url_soup2 = BeautifulSoup(get_url.content, "html.parser")
    dishes = url_soup2.find_all("h2", class_="gz-title")
    for dish in dishes:
        a_tag = dish.find("a")
        dishes_lst.append(a_tag.get("href"))
print(dishes_lst)
print("Number of dishes identified:",  len(dishes_lst))


exit()
# get title string for every dish and delete unnecessary strings
title_lst = []

for link in dishes_lst:
  get_url = requests.get(link)
  link_soup = BeautifulSoup(get_url.content, "html.parser")
  title = re.sub(" - La Ricetta di GialloZafferano", "\n", link_soup.title.string)
  title_lst.append(title)

title_lst_cleaned = []
for w in title_lst:
  title_clean = re.sub("Ricetta ", "", w)
  title_lst_cleaned.append(title_clean)
#print(title_lst_cleaned)

# for each recipe link: delete span tag, get paragraphs of html where recipe is explained, clean them from unwanted whitespaces, turn them into strings and join them
strings_lst = []
for link in dishes_lst:
  get_url = requests.get(link)
  link_soup = BeautifulSoup(get_url.content, "html.parser")
  for span in link_soup("span"):
    span.decompose()
  content = link_soup.find_all("div", class_="gz-content-recipe-step")
  full_text = []
  for step in content:
    p_tag = step.find("p")
    paragraph = re.sub(r"\s+", r" ", p_tag.get_text())
    paragraph = re.sub(r"\s([;:\.!\?\\-])", r"\1", paragraph)
    full_text.append(paragraph)
  strings_lst.append(re.sub(r"([;:\.!\?\\-])(\S)", r"\1 \2", "".join(full_text)))

#print(strings_lst)

# concatenate two lists element-wise

recipe_lst = [header + txt for header, txt in zip(title_lst_cleaned, strings_lst)]
print(recipe_lst)