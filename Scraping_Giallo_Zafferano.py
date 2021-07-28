from typing import Dict, Any, Union

from bs4 import BeautifulSoup

import logging
import os
import random
import requests
import re
import time
import urllib.request

# Setting up the logger
FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(format=FORMAT, level=logging.DEBUG)

logger = logging.getLogger()


class GialloZafferano():

    # sections = {"https://www.giallozafferano.it/ricette-cat/": 2}
    SECTIONS = {"https://www.giallozafferano.it/ricette-cat/": 383,
            "https://www.giallozafferano.it/ricette-cat/Antipasti/": 75,
            "https://www.giallozafferano.it/ricette-cat/Primi/": 86,
            "https://www.giallozafferano.it/ricette-cat/Secondi-piatti/": 66,
            "https://www.giallozafferano.it/ricette-cat/Contorni/": 19,
            "https://www.giallozafferano.it/ricette-cat/Dolci-e-Desserts/": 118,
            "https://www.giallozafferano.it/ricette-cat/Lievitati/": 25,
            "https://www.giallozafferano.it/ricette-cat/Piatti-Unici/": 30,
            "https://www.giallozafferano.it/ricette-cat/facili-e-veloci/": 74,
            "https://www.giallozafferano.it/ricette-cat/Primi/pasta/": 42,
            "https://www.giallozafferano.it/ricette-cat/Antipasti/facili-e-veloci/": 19,
            "https://www.giallozafferano.it/ricette-cat/Lievitati/Pizze-e-focacce/": 10,
            "https://www.giallozafferano.it/ricette-cat/Lievitati/pane/": 9,
            "https://www.giallozafferano.it/ricette-cat/Finger-food/": 45,
            "https://www.giallozafferano.it/ricette-cat/Torte-salate/": 11,
            "https://www.giallozafferano.it/ricette-cat/Al-forno/": 141,
            "https://www.giallozafferano.it/ricette-cat/Insalate/": 6,
            "https://www.giallozafferano.it/ricette-cat/Primi/Pasta-fresca/": 14,
            "https://www.giallozafferano.it/ricette-cat/Primi/facili-e-veloci/": 20,
            "https://www.giallozafferano.it/ricette-cat/Primi/pasta/grandi-classici/": 7,
            "https://www.giallozafferano.it/ricette-cat/Primi/pasta/Sfiziosi/": 30,
            "https://www.giallozafferano.it/ricette-cat/Primi/Gnocchi/": 7,
            "https://www.giallozafferano.it/ricette-cat/Primi/riso-cereali/": 16,
            "https://www.giallozafferano.it/ricette-cat/Secondi-piatti/Pesce/": 22,
            "https://www.giallozafferano.it/ricette-cat/Secondi-piatti/Vegetariani/": 12,
            "https://www.giallozafferano.it/ricette-cat/Dolci-e-Desserts/Biscotti/": 13,
            "https://www.giallozafferano.it/ricette-cat/Dolci-e-Desserts/piccola-pasticceria/": 37,
            "https://www.giallozafferano.it/ricette-cat/Dolci-e-Desserts/facili-e-veloci/": 18,
            "https://www.giallozafferano.it/ricette-cat/Dolci-e-Desserts/Torte/": 43,
            "https://www.giallozafferano.it/ricette-cat/al-cioccolato/": 30,
            "https://www.giallozafferano.it/ricette-cat/Dolci-e-Desserts/Torte/facili-e-veloci/": 5,
            "https://www.giallozafferano.it/ricette-cat/Marmellate-e-Conserve/Marmellate/": 4,
            "https://www.giallozafferano.it/ricette-cat/Carne/": 43,
            "https://www.giallozafferano.it/ricette-cat/Pesce/": 55,
            "https://www.giallozafferano.it/ricette-cat/Vegetariani/": 203
        }

    def __init__(self):
        None

    def create_folder(self, count, path="."):
        """
        Produces the path to the desired folder, departing from path.
        Creates the emtpy folder (warns if it already exists)
        :param count:
          number to differentiate the folders
        :param path:
          optional departing path (current folder if empty)
        :return:
          the path to the resulting folder
        """
        folder = os.path.join(path, "gf_it_"+str(count).zfill(4))
        if os.path.isdir(folder):
            logging.warning("Warning, folder %s exists", folder)
        else:
            os.mkdir(folder)
        return folder

    @staticmethod
    def get_contents(soup):
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
        # print(full_text)
        return "\n".join(full_text)

    @property
    def get_sections(self):
        return self.SECTIONS

    # def getFileName(title):
    #   """
    #   Get title string for the current recipe
    #   :param title:
    #           string title of the recipe
    #   :return:
    #           the name of the file to store the recipe to
    #   """
    #   f = ".".join([title.replace(" ", "_").replace("'", ""), "txt"])
    #   return f

    @staticmethod
    def get_ingredients(soup):
        """
        Get the necessary ingredients for the recipe
        :param soup:
            BeautifulSoup object
        :return:
            list of tab-separated ingredients (ingr<tab>quantity)
            for each recipe
        """
        # ingredients_lst = []
        ingredient_tag = soup.find_all("dd", class_="gz-ingredient")
        # on-the-fly list to append cleaned ingredients
        full_ingredients = ["ingredient\tquantity"]
        for t in ingredient_tag:
            ingredient = t.get_text().strip()
            ingredient = re.sub(r"([^\n\t]+)\s+([^\n\t]*)\s+([^\n\t]*[;:,\.!\?\\\-\%\(\)]*)\s+([^\n\t]*)",
                                r"\1 \2\3\t\4",
                                ingredient)
            ingredient = re.sub(r"([0-9½;,:\.!\?\\\-\%]+)\t([^\n\t]*)",
                                r"\t\1 \2", ingredient)
            ingredient = ingredient.replace(" \t", "\t")
            full_ingredients.append(ingredient)
        # append ingredients joined together to have an element with
        # the ingredients for every recipe
        return "\n".join(full_ingredients)

    def get_pages_list(self):
        for section in self.SECTIONS:
            for i in range(1, self.SECTIONS[section]):
                page = "".join([section, "page", str(i)])
                pages_lst.append(page)
        # print(pages_lst)
        logging.info("Number of section URLs produced: %i", len(pages_lst))
        return pages_lst

    def get_pictures(self, soup):
        """
        Looks for all the images illustrating the recipe steps
        :param soup:
        :return:
        a list with the URLs to every picture
        """
        prefix = "https://ricette.giallozafferano.it"
        tag = "picture"
        classes = ["gz-content-recipe-step-img gz-content-recipe-step-img-full",
            "gz-content-recipe-step-img gz-content-recipe-step-img-single"
            ]

        paths = []
        for cl in classes:
            image_tags = soup.find_all(tag, class_=cl)
            paths.extend(["/".join([prefix, t.find('img')['data-src']]) for t in image_tags])
        return paths

    def get_presentation(self, soup):
        """
        Get the header PRESENTAZIONE and paragraph with the presentation of the recipe
        :param soup:
                beautifulsoup object
        :return:
                string with paragraphs of the presentation
        """
        cl = "gz-innerwrapper gz-contentwrapper gz-fullbg gz-cabin-elevator-container"
        uppertitle_lst = []
        presentation_lst = []
        # title_presentation_lst = []

        # iterate over dict and find the tag with uppercase title and content
        presentation_tag = soup.find_all("div", class_=cl)
        # get title PRESENTAZIONE, add \n at the end to separate it from the text in the final list and append it in uppertitle_lst
        for tag in presentation_tag:
            uppertitle = tag.find("h2")
            uppercase_title = re.sub("PRESENTAZIONE", "PRESENTAZIONE\n", uppertitle.text)
        uppertitle_lst.append(uppercase_title)
        # print(uppertitle_lst)

        # get content and append it in presentation_lst
        for text in presentation_tag:
            content = text.find("p")
        presentation_lst.append(content.text)
        # print(presentation_lst)
        # exit(1)
        # concatenate the two lists element-wise in one title_presentation_lst
        # title_presentation_lst = [header + txt for header, txt in zip(uppertitle_lst, presentation_lst)]
        # return "\n".join(title_presentation_lst)
        return "\n".join(presentation_lst)

    @staticmethod
    def get_title(soup):
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

    @staticmethod
    def get_dishes_list(pages_lst):
        # for each page, get the section enclosed in the tag h2,
        # class and in that get a, href and append it to dishes_lst
        sleep_time = 5
        dishes_lst = []
        for url in pages_lst:
            logging.info("Identifying recipes from %s", url)
            get_url = requests.get(url)
            url_soup2 = BeautifulSoup(get_url.content, "html.parser")
            dishes = url_soup2.find_all("h2", class_="gz-title")
            for dish in dishes:
                a_tag = dish.find("a")
                dishes_lst.append(a_tag.get("href"))
            time.sleep(random.randrange(0, sleep_time))
        logging.info("Number of dishes found: %i", len(dishes_lst))
        print(dishes_lst)
        return dishes_lst

class GialloZafferanoEn(GialloZafferano):

    sections = {"https://www.giallozafferano.com/recipes-list/Appetizers/page2/": 2}

    # sections = {"https://www.giallozafferano.com/recipes-list/Appetizers/page2/": 16,
        # "https://www.giallozafferano.com/recipes-list/Appetizers/": 4,
        # "https://www.giallozafferano.com/recipes-list/First-Courses/": 5,
        # "https://www.giallozafferano.com/recipes-list/Main-Courses/": 5,
        # "https://www.giallozafferano.com/recipes-list/Sweets-and-Desserts/": 5,
        # "https://www.giallozafferano.com/recipes-list/Leavened-products/": 3
        # }

    @staticmethod
    def get_contents(soup):
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
            for tag in content.find_all("span", class_="num-step"):
                tag.string = re.sub(r"([0-9]+)", r"[\1]", tag.string)
                content.span.unwrap()
        # create a list on-the-fly, append cleaned paragraphs and join them to have an element for each recipe
        full_text = []
        for step in contents:
            p_tag = step.find("p")
            paragraph = re.sub(r"\s+", r" ", p_tag.get_text())
            paragraph = re.sub(r"\s([;:\.!\?\\-])", r"\1", paragraph)
            full_text.append(paragraph)
        print(full_text)
        return "\n".join(full_text)

    def get_ingredients(soup):
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
        full_ingredients = ["ingredient\tquantity"]
        for t in ingredient_tag:
            ingredient = t.get_text().strip()
            ingredient = re.sub(r"([^\n\t]+)\s+([^\n\t]*)\s+([^\n\t]*)\s+([^\n\t]*)\s*([^\n\t]*)", r"\1\t\2 \3 \4\t\5",
                                ingredient)
            ingredient = re.sub(r" (\([^\n\t]+\))", r"\t\1", ingredient)
            ingredient = ingredient.replace("\t to taste", "\tto taste")
            ingredient = ingredient.strip("\t")
            ingredient = ingredient.replace("\t-\t", "\t").replace(" - ", "\t-")
            full_ingredients.append(ingredient)
        # append ingredients joined together to have an element with the ingredients for every recipe
        return "\n".join(full_ingredients)

    def get_pictures(soup):
        """
        Looks for all the images illustrating the recipe steps
        :param soup:
        :return:
          a list with the URLs to every picture
        """
        prefix = "https://www.giallozafferano.com/"
        tag = "picture"
        cl = "gz-content-recipe-step-img gz-content-recipe-step-img-full"

        imageTags = soup.find_all(tag, class_=cl)
        paths = ["/".join([prefix, i.find('img')['data-src']]) for i in imageTags]
        return paths

    def get_presentation(soup):
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
        presentation_tag = soup.find_all("div",
                                         class_="gz-innerwrapper gz-contentwrapper gz-fullbg gz-cabin-elevator-container")
        # get title PRESENTAZIONE, add \n at the end to separate it from the text in the final list and append it in uppertitle_lst
        for tag in presentation_tag:
            uppertitle = tag.find("h2")
            uppercase_title = re.sub("PRESENTATION", "PRESENTATION\n", uppertitle.text)
        uppertitle_lst.append(uppercase_title)
        # print(uppertitle_lst)

        # get content and append it in presentation_lst
        for text in presentation_tag:
            content = text.find("p")
        presentation_lst.append(content.text)
        # print(presentation_lst)
        # exit(1)
        # concatenate the two lists element-wise in one title_presentation_lst
        # title_presentation_lst = [header + txt for header, txt in zip(uppertitle_lst, presentation_lst)]
        # return "\n".join(title_presentation_lst)
        return "\n".join(presentation_lst)

    @staticmethod
    def get_title(soup):
        """
        Get title string for the current recipe
        :param soup:
                beautifulsoup object
        :return:
                string title without necessary fragments
        """
        title = re.sub(" - Italian recipes by GialloZafferano", "\n", soup.title.string)
        return title

####
# main process
###
gz = GialloZafferano()
pages_lst = gz.get_pages_list()
dishes_lst = gz.get_dishes_list(pages_lst)

total_dishes = len(dishes_lst)

counter = 0
for link in dishes_lst:
    if counter % 10 == 0:
        logging.info("Processing recipe %i/%i", counter, total_dishes)

    folder = gz.create_folder(counter)
    counter += 1

    # getting the recipe contents from the website
    get_url = requests.get(link)
    link_soup = BeautifulSoup(get_url.content, "html.parser")

    # getting the title, presentation, ingredients and contents

    recipeTitle = gz.get_title(link_soup)
    # logging.info("Storing recipe %s", recipeTitle)
    # title file
    fileTitle = os.path.join(folder, "title.txt")
    with open(fileTitle, "w") as f:
        f.write("\n".join([recipeTitle, link]))

    # presentation file
    recipePresentation = gz.get_presentation(link_soup)
    filePres = os.path.join(folder, "presentation.txt")
    with open(filePres, "w") as f:
        f.write(recipePresentation)

    # ingredients
    recipeIngredients = gz.get_ingredients(link_soup)
    fileIngredients = os.path.join(folder, "ingredients.txt")
    with open(fileIngredients, "w") as f:
        f.write(recipeIngredients)

    # preparation
    recipeContents = gz.get_contents(link_soup)
    filePreparation = os.path.join(folder, "preparation.txt")
    with open(filePreparation, "w") as f:
        f.write(recipeContents)

    # pictures
    recipePictures= gz.get_pictures(link_soup)
    for pict in recipePictures:
        filePict = os.path.join(folder, pict[pict.rfind("/")+1:])
        urllib.request.urlretrieve(pict, filePict)

    # sleep for a random time in [0, 10] secs to avoid overleading the server
    time.sleep(random.randrange(0, 10))
    # exit()