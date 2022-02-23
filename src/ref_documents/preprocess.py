## A general preprocessing template
## Some functions taken from https://towardsdatascience.com/nlp-text-preprocessing-a-practical-guide-and-template-d80874676e79

import os
import time
import threading
import numpy as np
import pandas as pd
from pycontractions import Contractions
from bs4 import BeautifulSoup

# Gensim, nltk
import gensim.downloader as api
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from gensim import corpora, models
from nltk.stem import WordNetLemmatizer, SnowballStemmer
from nltk.stem.porter import *
import gensim
import nltk

# Configure pdfminer
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LTTextBoxHorizontal

DEBUG = False
N_WORKERS = 4
REF_TEXT_DIR = './data/ref_text'
SAVE_DIR = './data/preprocessed'

def log_error(error, worker, university, submission, errmsg):
    if not os.path.isdir('./logs/preprocessing'):
        os.makedirs('./logs/preprocessing')

    try:
        with open('logs/preprocessing/{}_error_{}.csv'.format(error, worker), 'a') as f:
            f.write('{},{},{},{}\n'.format(worker, university, submission, errmsg))
    except Exception as e:
        print('[{}] Error occurred whilst writing error log file'.format(worker))

def read_text(file):
    with open(file, 'r') as f:
        file = f.read()
    
    return file

def remove_numbers(str):
    return re.sub(r'\d+', '', str)

def remove_punctuation(str):
    return re.sub(r'[^\w\s]', ' ', str)

def expand_contractions(text):
    text = list(cont.expand_texts([text], precise=True))[0]
    return text

def lemmatize_stemming(text):
    token = WordNetLemmatizer().lemmatize(text, pos='v')
    return stemmer.stem(token)

def preprocess(text):
    result = []

    text = remove_numbers(text)

    for token in gensim.utils.simple_preprocess(text, deacc=True):
        if token not in gensim.parsing.preprocessing.STOPWORDS and len(token) > 3 and token not in ['http', 'https']:
            result.append(lemmatize_stemming(token))
    return result

def preprocess_ref_submissions(worker, universities):
    summary_of_impact = re.compile("(1\s*summary\s*of\s*the\s*impact\s*)(.*)(\s*2\s*underpinning\s*research)")
    underpinning_research = re.compile("(2\s*underpinning\s*research\s*)(.*)(\s*3\s*references\s*to\s*the\s*research)")
    details_of_impact = re.compile("(4\s*details\s*of\s*the\s*impact)(.*)(\s*5\s*sources\s*to\s*corroborate\s*the\s*impact)")

    for university in universities:
        if not os.path.isdir('./data/preprocessed/{}'.format(university)):
            os.makedirs('./data/preprocessed/{}'.format(university))

        # Save preprocessed PDF as text file
        with open('./data/preprocessed/{}/{}_processed.csv'.format(university, worker), 'a') as f:
            print('--- WORKER {} PROCESSING {} ---'.format(worker, university))
            for submission in os.listdir('{}/{}/'.format(REF_TEXT_DIR, university)):
                try:
                    pdf_string = read_text('{}/{}/{}'.format(REF_TEXT_DIR, university, submission))
                    pdf_string = pdf_string.lower()
                    pdf_string = remove_punctuation(pdf_string)

                    summary = summary_of_impact.search(pdf_string)
                    underpinning = underpinning_research.search(pdf_string)
                    details = details_of_impact.search(pdf_string)

                    combined = []

                    if summary:
                        summary = summary.group(0)
                        summary = summary.replace('summary of the impact', '').replace('underpinning research', '')
                        summary = preprocess(summary)
                        combined += summary
                    
                    if underpinning:
                        underpinning = underpinning.group(0)
                        underpinning = underpinning.replace('underpinning research', '').replace('references to the research', '')
                        underpinning = preprocess(underpinning)
                        combined += underpinning

                    if details:
                        details = details.group(0)
                        details = details.replace('details of the impact', '').replace('sources to corroborate the impact', '')
                        details = preprocess(details)
                        combined += details
                except Exception as e:
                    print('Error occured whilst preprocessing {}\n{}'.format(submission, e))
                    log_error('preprocessing', worker, university, submission, e)
                    continue

                try:
                    f.write('{}\t{}\t{}\t{}\t{}\n'.format(submission, summary, underpinning, details, combined))    
                except Exception as e:
                    print('Error occured whilst recording {}\n{}'.format(submission, e))
                    log_error('writing', worker, university, submission, e)

if __name__ == '__main__':
    nltk.download('wordnet')
    nltk.download('stopwords')
    stemmer = SnowballStemmer("english", ignore_stopwords=True)
    # model = api.load("glove-twitter-25")
    # cont = Contractions(kv_model=model)
    # cont.load_models()

    universities = os.listdir(REF_TEXT_DIR)
    local_universities = [[] for x in range(N_WORKERS)]

    if DEBUG:
        preprocess_ref_submissions(0, [universities[0]])
    else:
        if N_WORKERS < 1:
            N_WORKERS = 1

        j = 0                       
        for university in universities:           
            if j >= N_WORKERS: 
                j = 0

            local_universities[j].append(university)
            j += 1

        try:
            threads = []
            for i in range(N_WORKERS):
                threads.append(threading.Thread(target=preprocess_ref_submissions, args=(i, local_universities[i])))

            for thread in threads:
                thread.setDaemon(True)
                thread.start()
                time.sleep(2)

            main_thread = threading.currentThread()
            for t in threading.enumerate():
                if t is main_thread:
                    continue
                t.join()
        except (KeyboardInterrupt, SystemExit):
            print('\n\nReceived keyboard interrupt, quitting threads.')