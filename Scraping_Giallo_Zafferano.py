from bs4 import BeautifulSoup
import requests
import re

sections = {"https://www.giallozafferano.it/ricette-cat/": 2}


def getContents(soup):
  """
  Get the contents of the recipe, get paragraphs of html
  where recipe is explained, clean them from unwanted whitespaces, turn them
  into strings and join them. Add square brackets to numbered steps 
  and unwrap them from span tag. 
  :param soup:
      beautifulsoup object
  :return:
      string with the contents of the recipe
  """
  contents_lst = []
  contents = soup.find_all("div", class_="gz-content-recipe-step")
  # enclose string of span tag in square brackets and unwrap it from the span tag
  for content in contents:
      for tag in content.find_all("span"):
          tag.string = re.sub(r"([0-9]+)", r"[\1]", tag.string)
          content.span.unwrap()
  # create a list on-the-fly, append cleaned paragraphs and join them to have an element for each recipe
  full_text = []
  for step in contents:
      p_tag = step.find("p")
      paragraph = re.sub(r"\s+", r" ", p_tag.get_text())
      paragraph = re.sub(r"\s([;:\.!\?\\-])", r"\1", paragraph)
      full_text.append(paragraph)
  contents_lst.append(re.sub(r"([;:\.!\?\\-])(\S)", r"\1 \2", "".join(full_text)))
  titolo = "PREPARAZIONE\n"
  titolo += '{0}'
  contents_lst = [titolo.format(i) for i in contents_lst]
  return "\n".join(contents_lst)


def getFileName(title):
  """
  Get title string for the current recipe
  :param title:
          string title of the recipe
  :return:
          the name of the file to store the recipe to
  """
  f = ".".join([title.replace(" ", "_").replace("'", ""), "txt"])
  return f


def getIngredients(soup):
  """
  Get the necessary ingredients for the recipe
  :param soup:
        BeautifulSoup object
  :return:
        list of ingredients with header INGREDIENTI\n
        for each recipe
  """
  ingredients_lst = []
  ingredient_tag = soup.find_all("dd", class_="gz-ingredient")
  # on-the-fly list to append cleaned ingredients
  full_ingredients = []
  for t in ingredient_tag:
      ingredient = t.get_text().strip()
      ingredient = re.sub(r"([^\n\t]+)\s+([^\n\t]*)\s+([^\n\t]*[;:,\.!\?\\\-\%\(\)]*)\s+([^\n\t]*)", r"\1 \2\3\t\4",
                          ingredient)
      ingredient = re.sub(r"([0-9½;,:\.!\?\\\-\%]+)\t([^\n\t]*)", r"\t\1 \2", ingredient)
      ingredient = ingredient.replace(" \t", "\t")
      full_ingredients.append(ingredient)
  # append ingredients joined together to have an element with the ingredients for every recipe
  ingredients_lst.append("\n".join(full_ingredients))
  titolo = "INGREDIENTI\n"
  titolo += '{0}'
  ingredients_lst = [titolo.format(i) for i in ingredients_lst]
  return "\n".join(ingredients_lst)

def getPresentation(soup):
  """
  Get the header PRESENTAZIONE and paragraph with the presentation of the recipe
  :param soup:
            beautifulsoup object
  :return:
            string with uppercase title PRESENTAZIONE\n and paragraph of the presentation
  """
  uppertitle_lst = []
  presentation_lst = []
  title_presentation_lst = []

  # iterate over dict and find the tag with uppercase title and content
  presentation_tag = soup.find_all("div", class_="gz-innerwrapper gz-contentwrapper gz-fullbg gz-cabin-elevator-container")
  # get title PRESENTAZIONE, add \n at the end to separate it from the text in the final list and append it in uppertitle_lst
  for tag in presentation_tag:
      uppertitle = tag.find("h2")
      uppercase_title = re.sub("PRESENTAZIONE", "PRESENTAZIONE\n", uppertitle.text)
  uppertitle_lst.append(uppercase_title)
  #print(uppertitle_lst)

  # get content and append it in presentation_lst
  for text in presentation_tag:
      content = text.find("p")
  presentation_lst.append(content.text)
  # print(presentation_lst)

  # concatenate the two lists element-wise in one title_presentation_lst
  title_presentation_lst = [header + txt for header, txt in zip(uppertitle_lst, presentation_lst)]
  return "\n".join(title_presentation_lst)

def getTitle(soup):
  """
  Get title string for the current recipe
  :param soup:
          beautifulsoup object
  :return:
          string title without necessary fragments
  """
  title = re.sub(" - La Ricetta di GialloZafferano", "\n", soup.title.string)
  title = re.sub("Ricetta ", "", title).strip()
  return title


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
print("Number of dishes found:", len(dishes_lst))

for link in dishes_lst:
  # getting the recipe contents from the website
  get_url = requests.get(link)
  link_soup = BeautifulSoup(get_url.content, "html.parser")

  # getting the title, presentation, ingredients and contents
  recipeTitle = getTitle(link_soup)
  recipePresentation = getPresentation(link_soup)
  recipeIngredients = getIngredients(link_soup)
  recipeContents = getContents(link_soup)

  file_name = getFileName(recipeTitle)
  with open(file_name, "w") as f:
    f.writelines([
        recipeTitle, "\n",
        recipePresentation, "\n",
        recipeIngredients, "\n",
        recipeContents
        ])
  print("Storing recipe", recipeTitle)
  # print(recipeContents)
  exit()