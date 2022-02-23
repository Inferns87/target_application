import re
import string

from num2words import num2words
from pycontractions import Contractions
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer, SnowballStemmer, PorterStemmer


sbstemmer = SnowballStemmer("english", ignore_stopwords=True)
ptstemmer = PorterStemmer()
lemmetizer = WordNetLemmatizer()
cont = Contractions(api_key="glove-twitter-100")

STOP_WORDS = set(stopwords.words('english'))

def expand_contractions(texts, precision):
    if len(texts > 0):
        contracted = [cont.expand_texts(texts, Precision=precision)]
    else:
        contracted = [cont.expand_texts(texts, Precision=precision)][0]
    return contracted


def remove_stop_words(text, stop_words=STOP_WORDS):
    tokens = word_tokenize(text)
    filtered_text = [w for w in tokens if not w in stop_words]
    return filtered_text


def remove_single_character_words(text):
    words = text.split(" ")
    filtered_text = [word for word in words if len(word) > 0]
    return " ".join(filtered_text)


def remove_trailing_whitespace(text):
    clean_text = " ".join(text.strip().split())
    return clean_text


def remove_punctuation(text):
    punctuation = str.maketrans('', '', string.punctuation)
    clean_text = [word.translate(punctuation) for word in text]
    return " ".join(clean_text)


def remove_url(text):
    ## Modified from https://github.com/amansrivastava17/text-preprocess-python/blob/master/cleaner.py
    urlfree = []
    for word in text.split():
        if not word.startswith("www"):
            urlfree.append(word)
        elif not word.startswith("http"):
            urlfree.append(word)
        elif not word.startswith("https"):
            urlfree.append(word)
        elif not word.endswith(".html"):
            urlfree.append(word)
    urlfree = " ".join(urlfree)

    urls = re.finditer(r'http[\w]*:\/\/[\w]*\.?[\w-]+\.+[\w]+[\/\w]+', urlfree)
    for i in urls:
        urlfree = re.sub(i.group().strip(), '', urlfree)
    return urlfree


def remove_numbers(text):
    clean_text = re.sub(r'\d+', '', text)
    return clean_text


def numbers_to_words(text):
    tokens = word_tokenize(text)
    filtered_text = []
    for token in tokens:
        try:
            number = num2words(token)
            filtered_text.append(number)
        except:
            filtered_text.append(token)
            continue
    return " ".join(filtered_text)


def lemmatize_text(text):
    tokens = word_tokenize(text)
    lemmatized_text = lemmetizer.lemmatize(tokens, pos='v')
    return lemmatized_text


def stem_text(text, stemmer="snowball"):
    tokens = word_tokenize(text)
    if stemmer == "snowball":
        stemmed_text = " ".join([sbstemmer.stem(word) for word in tokens])
    else:
        stemmed_text = " ".join([ptstemmer.stem(word) for word in tokens])
    return stemmed_text
