import os
import re
import glob
import json
import string
import nltk

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

stopwords.words('english')

lemma = WordNetLemmatizer()

ROOT = os.getcwd().split("src")[0]


def write_json_file(data, file):
    '''
    Write data to JSON file
    '''

    with open(f"{file}", "w") as f:
        json.dump(data, f)


def read_json_file(file):
    '''
    Read data from JSON file
    '''

    with open(f"{file}", "r") as f:
        data = json.load(f)
    
    return data


def spacy_tokenizer(parser, stopwords, punctuations, sentence):
    mytokens = parser(sentence)
    mytokens = [ word.lemma_.lower().strip() if word.lemma_ != "-PRON-" else word.lower_ for word in mytokens ]
    mytokens = [ word for word in mytokens if word not in stopwords and word not in punctuations ]
    mytokens = " ".join([i for i in mytokens])
    return mytokens


def preprocess(string):
    '''
    Preprocesses document. Returns a set of preprocessed sentences.
    '''

    stop_words = list(stopwords.words('english'))
    custom_stop_words = [
        'doi', 'preprint', 'copyright', 'peer', 'reviewed', 'org', 'https', 'et', 'al', 'author', 'figure', 
        'rights', 'reserved', 'permission', 'used', 'using', 'biorxiv', 'medrxiv', 'license', 'fig', 'fig.', 
        'al.', 'Elsevier', 'PMC', 'CZI', 'www'
    ]

    for w in custom_stop_words:
        if w not in stop_words:
            stop_words.append(w)
    
    preprocessed_sentences = []
    sentences = string.split(".")
    for sentence in sentences:
        sentence = sentence.lower()
        sentence = re.sub(r'http\S+', '', sentence)  # remove links
        sentence = re.sub(r'[^a-zA-Z ]', '', sentence) # Remove numbers and punctuation
        sentence = ''.join(sentence) # Remove trailing whitespace
        tokens = word_tokenize(sentence)
        tokens = [word for word in tokens if word not in stop_words]
        tokens = [lemma.lemmatize(word=word, pos="v") for word in tokens]
        tokens = [word for word in tokens if len(word) > 2]
        if len(tokens) < 4:
            continue
        sentence = ' '.join(tokens)
        preprocessed_sentences.append(sentence)
    return preprocessed_sentences


def main():
    chapters = [
        '240 Industrial Strategy White Paper',
        'References 1',
        '240 Britain and the world',
        'Places 214',
        'Business Environment 162',
        'Infrastructure 126',
        'People 92',
        'Ideas 56',
        'Grand Challenges 30',
        'Introduction 8',
        'Foreword from the Prime Minister'
    ]

    with open(
        f"{ROOT}/data/industrial_strategy/raw/industrial-strategy-white-paper-web-ready-version.txt",
        "r",
        encoding="utf-8"
    ) as f:
         _file = re.sub(r'[^A-Za-z0-9 .]+', ' ', f.read())

    strategy_chapters = {}
    for chapter in chapters:
        # Remove all content before "Indusrtial Strategy White Paper"
        if chapter == "240 Industrial Strategy White Paper":
            _file = _file.split(chapter)[1]
        # Remove all content after "References"
        elif chapter == "References 1":
            _file = _file.split(chapter)[0]
        # Add each chapter to the dicationary x
        else:
            strategy_chapters[chapter] = _file.split(chapter)[1]

    strategy_sentences = []
    for chapter in strategy_chapters.keys():
        preprocessed_sentences = preprocess(strategy_chapters[chapter])
        strategy_sentences.extend(preprocessed_sentences)
        doc = {
            "title": chapter,
            "body": preprocessed_sentences
        }
        write_json_file(doc, f"{ROOT}/data/industrial_strategy/json/preprocessed/{chapter}.json")
    doc = {
        "title": "industrial_strategy",
        "body": strategy_sentences
    }
    write_json_file(doc, f"{ROOT}/data/industrial_strategy/json/preprocessed/industrial_strategy.json")



if __name__ == "__main__":
    main()
