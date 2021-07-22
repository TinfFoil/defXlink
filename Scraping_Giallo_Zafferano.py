from bs4 import BeautifulSoup
import requests
import re

sections = {"https://www.giallozafferano.it/ricette-cat/": 2}


def getContents(soup):
  """
  Get the contents of the recipe. Delete span tag, get paragraphs of html
  where recipe is explained, clean them from unwanted whitespaces, turn them
  into strings and join them
  :param soup:
      beautifulsoup object
  :return:
      string with the contents of the recipe
  """
  for span in soup("span"):
     span.decompose()
  content = soup.find_all("div", class_="gz-content-recipe-step")
  full_text = []
  for step in content:
     p_tag = step.find("p")
     paragraph = re.sub(r"\s+", r" ", p_tag.get_text())
     paragraph = re.sub(r"\s([;:\.!\?\\-])", r"\1", paragraph)
     full_text.append(paragraph)
  return re.sub(r"([;:\.!\?\\-])(\S)", r"\1 \2", "".join(full_text))


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
  :return:

  """
  # TODO
  return ""

def getPresentation(soup):
  """
  Get the header PRESENTATION and paragraph with the presentation of the recipe
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
  # get title PRESENTATION, add \n at the end to separate it from the text in the final list and append it in uppertitle_lst
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