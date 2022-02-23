import os
import re
import glob
import json
import string
import nltk

from pathlib import Path

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
    Path(f"{ROOT}/data/papers/json/preprocessed/arxiv").mkdir(parents=True, exist_ok=True)
    Path(f"{ROOT}/data/papers/json/preprocessed/scopus").mkdir(parents=True, exist_ok=True)
    Path(f"{ROOT}/data/papers/json/preprocessed/unknown").mkdir(parents=True, exist_ok=True)
    papers = glob.glob(f"{ROOT}/data/papers/json/raw/*/*.json")
    print(f"Iterating through {len(papers)} papers")
    for i, paper in enumerate(papers):
        if i % 10 == 0:
            print(f"{i / len(papers) * 100}% complete")
        paper_type = None
        if "Arxiv" in paper:
            paper_type = "arxiv"
        elif "Scopus" in paper:
            paper_type = "scopus"
        else:
            paper_type = "unknown"
        # Read document
        json_paper = read_json_file(paper)
        file_name = paper.split("/")[-1].replace(".json", "")
        if os.path.isfile(f"{ROOT}/data/papers/json/preprocessed/{paper_type}/{file_name}.json"):
            continue
        paper_affiliations = json_paper['description']['affiliations']
        if "author" in json_paper['description']:
            paper_authors = json_paper['description']['author']
        if "authors" in json_paper['description']:
            paper_authors = json_paper['description']['authors']
        paper_title = json_paper['description']['affiliations']
        paper_abstract = json_paper['description']['abstract']
        body = []
        for element in json_paper['main-text']:
            if element["type"] == "paragraph":
                body.append(element['text'])
        body_string = " ".join(body)
        body_preprocessed = preprocess(body_string)
        doc = {
            "pdf_name": json_paper['_name'].replace(".pdf", ""),
            "title": paper_title,
            "authors": paper_authors,
            "affiliations": paper_affiliations,
            "abstract": paper_abstract,
            "body": body_preprocessed
        }
        write_json_file(doc, f"{ROOT}/data/papers/json/preprocessed/{paper_type}/{file_name}.json")


if __name__ == "__main__":
    main()
