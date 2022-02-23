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
        sentence = re.sub(r"http\S+", "", sentence)  # remove links
        sentence = re.sub(r"[^a-zA-Z ]", "", sentence) # Remove numbers and punctuation
        sentence = "".join(sentence) # Remove trailing whitespace
        tokens = word_tokenize(sentence)
        tokens = [word for word in tokens if word not in stop_words]
        tokens = [lemma.lemmatize(word=word, pos="v") for word in tokens]
        tokens = [word for word in tokens if len(word) > 2]
        if len(tokens) < 4:
            continue
        sentence = " ".join(tokens)
        preprocessed_sentences.append(sentence)
    return preprocessed_sentences


def main():
    papers = glob.glob(f"{ROOT}/data/ref_submissions/json/raw/**/*.json",
                       recursive=True)
    for i, paper in enumerate(papers):
        if i % 10 == 0:
            print(f"{i / len(papers) * 100}% complete")
        # Read document
        json_paper = read_json_file(paper)
        file_name = json_paper["_name"].replace(".pdf", "")
        if os.path.isfile(f"{ROOT}/data/ref_submissions/json/preprocessed/{file_name}.json"):
            continue
        doc = {
            "chapters": {}
        }
        for element in json_paper["main-text"]:
            if element["name"] == "university":
                doc["university"] = element["text"]
            elif element["name"] == "title-of-case-study":
                doc["title-of-case-study"] = element["text"]
            elif element["name"] == "impact-summary":
                if "impact-summary" not in doc["chapters"].keys():
                    doc["chapters"]["impact-summary"] = [element["text"]]
                else:
                    doc["chapters"]["impact-summary"].append(element["text"])
            elif element["name"] == "details-details":
                if "impact-details" not in doc["chapters"].keys():
                    doc["chapters"]["impact-details"] = [element["text"]]
                else:
                    doc["chapters"]["impact-details"].append(element["text"])
            elif element["name"] == "details-summary":
                if "impact-summary" not in doc["chapters"].keys():
                    doc["chapters"]["impact-summary"] = [element["text"]]
                else:
                    doc["chapters"]["impact-summary"].append(element["text"])
            elif element["name"] == "underpinning-researc":
                if "underpinning-researc" not in doc["chapters"].keys():
                    doc["chapters"]["underpinning-researc"] = [element["text"]]
                else:
                    doc["chapters"]["underpinning-researc"].append(element["text"])

        for chapter in doc["chapters"].keys():
            body_string = " ".join(doc["chapters"][chapter])
            doc["chapters"][chapter] = preprocess(body_string)

        write_json_file(doc, f"{ROOT}/data/ref_submissions/json/preprocessed/{file_name}.json")


if __name__ == "__main__":
    main()
