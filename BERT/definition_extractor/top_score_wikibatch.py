#
#   Look at a folder with txt files extracted from wikipedia (see wiki_parser_*.py)
#   Use the first line as the name of the glossary item to create
#   Treat the rest of the text as input to find the best sentence that defines the item,
#   using the model from Navigli.
#
# TODO: use optionally local or remote db (change in port and user settings)
#       - language param is used to query DB and to load the proper model. We could pass an optional param to filter for specific ID or Name (better)
#       - consider an optional param to 'force update' to find updated data file and re-extract definitions 

from importlib import metadata
from unittest import skip
from datasets import load_dataset, Dataset, DatasetDict
from transformers import AutoTokenizer, TextClassificationPipeline, DataCollatorWithPadding, AutoModelForSequenceClassification
import numpy as np
from datasets import load_metric
import pandas as pd
import spacy
import glob
import os
import sys
from operator import itemgetter
from spacy.tokens import Doc
from spacy.language import Language
import signal
import logging
import pickle
import csv
import mysql.connector
from os import environ as env
import argparse


class Application:

    def __init__( self ):
        signal.signal( signal.SIGINT, lambda signal, frame: self._signal_handler() )
        self.terminated = False
        logging.basicConfig(
            encoding='utf-8', 
            format='%(asctime)s - %(levelname)s: %(message)s', 
            level=logging.INFO,
            handlers=[
                logging.FileHandler("wikiDefinition.log", encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )

    def _signal_handler( self ):
        print("Waiting for current file to be processed then exiting..")
        self.terminated = True

    def is_blank(self, s):
        return bool(not s or s.isspace())


    def connect_to_db(self):        
        host=env['HOST'],
        user=env['DBUSER'],
        password=env['DBPASSWORD'],
        database=env['DB']
        mydb = mysql.connector.connect(          
          host=host,
          user=user,
          password=password,
          database=database,
          port=3306 #port=3307
        )
        return mydb

    def get_filenames_from_pickle(self, path_to_folder, pickle_name):
        # read pickle with list of files to process
        #  page_tuple = (page.pageid, page.title, main_image)
        if os.path.isfile(pickle_name):
            with open(pickle_name, 'rb') as fp:
                metadata = pickle.load(fp)
            basepath = os.path.join(path_to_folder, self.lang)
            #files = [os.path.join(basepath,str(tple[0])+".txt") for tple in metadata]
            files = [str(tple[0]) for tple in metadata]
        else:
            files = glob.glob(glob.escape(path_to_folder) + "/*.txt")
        return files

    def write_tuples_to_csv(self, tuples, base_name):
        output_csv_name = 'wikibatch' + base_name + '.csv'
        with open(output_csv_name, 'a+', newline='', encoding='utf-8') as output_csv:            
            writer = csv.writer(output_csv, delimiter=",")
            for data in tuples:
                # tuple is: file_id, highest_score[0], second_highest_def, title
                writer.writerow([data[0].rstrip(),data[1].rstrip(),data[2].rstrip(),data[3].rstrip()])


    def get_filenames_from_db(self, lang):
        sql_read = "SELECT id FROM items WHERE language = '{0}' and definition1 is null LIMIT 100".format(lang)
        mydb = self.connect_to_db()
        mycursor = mydb.cursor()
        mycursor.execute(sql_read)
        myresult = mycursor.fetchall()
        records_to_write = []
        for record in myresult:
              records_to_write.append(str(record[0]))
        mycursor.close()
        print("found {} records to update".format(len(records_to_write)))
        return records_to_write


    def write_tuples_to_db(self, tuples):
        mydb = self.connect_to_db()        
        sql = "UPDATE items SET definition1 = %s, definition2= %s WHERE id = %s"
        # do this in a loop. Slow but safe        
        for row in tuples:
            # row is 0=id,1=def1,2=def2
            if row[2] == "\n":
                def2 = ''
            else:
                def2 =row[2]
            val = (row[1], def2, row[0]) # id is the last value, it's in the WHERE clause
            mycursor = mydb.cursor()                
            mycursor.execute(sql, val)
            mydb.commit()
        logging.info("updated {0} records".format(len(tuples)))

    def batch(self, iterable, n=1):
        l = len(iterable)
        for ndx in range(0, l, n):
            yield iterable[ndx:min(ndx + n, l)]


    def MainLoop( self ):  
        print("This program will extract definitions from text files (supposedly from wikipedia), and store results in a db or csv file.")
        parser = argparse.ArgumentParser()
        parser.add_argument('--path', required=False, default="data", type=str, metavar='PATH', help='The target path (where data files to analyze are located)')
        parser.add_argument('--lan', required=False, default="it", type=str, metavar='LANGUAGE', help='The language of the model to use (e.g. en, it)')
        parser.add_argument('--pickle', required=False, default="", type=str, metavar='PICKLE', help='Pickle name that contains metadata about files. Leave blank to use local database')
        
        args = parser.parse_args()
        path_to_folder = args.path
        self.lang = args.lan
        pickle_name_raw = args.pickle

        #choose the language in which we have data:
        #lang = input("enter the language code for the data to analyze: (supported: en, it)\n")
        #self.lang = lang
        usedb = False
        single_file = False
        
        #choose a path to get list of files
        #path_to_folder = input("Enter the path to the file(s) to analyze:\n")
        if os.path.exists(path_to_folder) == False:
            sys.exit("sorry, the specified folder does not exist.")

        if path_to_folder.endswith('.txt'):
            single_file = True
            files_to_process = [path_to_folder]
        else:
            # choose a pickle with list of files
            # pickle_name_raw = input("Enter the pickle name (without extension) that contains metadata about files: (leave blank to use local DB)\n")
            if pickle_name_raw == None or pickle_name_raw.strip() == '':
                usedb = True
                files_to_process = self.get_filenames_from_db(self.lang)
            else:
                pickle_name = os.path.join(path_to_folder,pickle_name_raw+".pickle")
                files_to_process = self.get_filenames_from_pickle(path_to_folder, pickle_name)

        if self.lang == 'en':
            nlp = spacy.load("en_core_web_md")
            nlp.add_pipe('sentencizer', before='parser')

            sentences = []

            checkpoint = 'bert-base-cased'
            tokenizer = AutoTokenizer.from_pretrained(checkpoint)

            model = AutoModelForSequenceClassification.from_pretrained('\\users\\fede9\\MTData\\saved_model_EN\\')

            pipe = TextClassificationPipeline(model=model, tokenizer=tokenizer, return_all_scores=True)
        elif self.lang == 'it':
            nlp = spacy.load("it_core_news_md")
            nlp.add_pipe('sentencizer', before='parser')

            checkpoint = 'bert-base-multilingual-cased'
            tokenizer = AutoTokenizer.from_pretrained(checkpoint)
            model = AutoModelForSequenceClassification.from_pretrained('\\users\\fede9\\MTData\\saved_model_IT\\')
            # BUGBUG: with Transformer > 4.19, return_all_scores is deprecated, 
            # and using top_k=None doesn't yield the same results.
            # Perhaps we need to look at this line and debug:
            #   scores = predictions[idx][1]['score']
            #pipe = TextClassificationPipeline(model=model, tokenizer=tokenizer, top_k=None)
            pipe = TextClassificationPipeline(model=model, tokenizer=tokenizer, return_all_scores=True)
        else:
            sys.exit("sorry, we don't have a model for language %s", self.lang)

        for batch in self.batch(files_to_process, 5):
            tuples = []        
            for file_id in batch:
                #open file, sentencize and create list of sentences
                sub_folder = os.path.join(path_to_folder, self.lang)
                if file_id.endswith('txt'):
                    path_to_text = os.path.join(sub_folder, str(file_id))
                else:
                    path_to_text = os.path.join(sub_folder, str(file_id)+".txt")
                if os.path.isfile(path_to_text) == False:
                    logging.warn("!! Cannot find file {}".format(path_to_text))
                    continue
                with open(path_to_text, 'r', encoding='utf-8') as f:
                    logging.info('## processing file: {} ##'.format(path_to_text))
                    sentences = []
                    lines= f.readlines() 
                    #HACK: sentencizer is too optimistic, and ends up creating overly long sentences when a file contains a list of items in many lines.
                    for line in lines:
                        doc = nlp(line)
                        linesents = [str(sent) for sent in list(doc.sents)]
                        sentences.extend(linesents)

                title = sentences[0]
                if title.find(':') > -1 or title.find('(disambigua)') > -1:    #not interested in wiki categories and other meta-entries, only individual articles
                    logging.info("skipping '{}' since it's not a full article".format(title))
                    continue 

                predictions = pipe(sentences)

                final_scores = []

                #print highest score in list of sentences using pre-trained model bert trained with Navigli's corpus
                for idx, sentence in enumerate(sentences):
                    scores = predictions[idx][1]['score']
                    final_scores.append((sentence, scores))

                sorted_scores = sorted(final_scores, key=itemgetter(1))
                #print(sorted_scores)

                highest_index = -1
                highest_score = sorted_scores[-1]
                while self.is_blank(sorted_scores[highest_index][0]):
                    highest_index -= 1

                highest_score = sorted_scores[highest_index]
                second_highest = sorted_scores[highest_index-1]
                if second_highest[0].isspace():
                    second_highest_def ='' # do not write a \n or other spurious chars, just an empty string.
                else:
                    second_highest_def = second_highest[0]
                logging.info('File: {}, Item: {}, Definition: {}, Second Def:{}'.format(path_to_text, title, highest_score,second_highest))
            
                data = (file_id, highest_score[0], second_highest_def, title)
                tuples.append(data)            
            #end for
            if usedb:
                self.write_tuples_to_db(tuples)
            elif single_file:
                print('Item: {}, Definition: {}, Second Def:{}'.format(data[3],data[1],data[2]))
            else: # write to csv file
                self.write_tuples_to_csv(tuples, pickle_name_raw)
            if self.terminated:
                    break
        #end batch


app = Application()
app.MainLoop()

print( "Exiting..." )