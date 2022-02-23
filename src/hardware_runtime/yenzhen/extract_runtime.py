import os
import re
import csv
import sys
import math
import glob
import nltk
import numpy as np
import pandas as pd

nltk.download("punkt")
ROOT = os.getcwd().split("src")[0]

"""
Based on output of Yenzhen"s internship

Need to replace with more robust information extraction algorithms
"""


def decision(tree, sentence):
    try:
        sentence = sentence.split()
        for i in tree:
            if i[0] in sentence and i[1]==1:
                return 1
        return 0
    except Exception as e:
        print(f"Sentence {sentence}\nError: {e}")


def word2num(sentence):
    wordlist = ["one", "two", "three", "four", "five",  "six", "seven", "nine", "ten", "several"]
    numlist = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "3"]
    for i in range(len(wordlist)):
        sentence = re.sub(wordlist[i], numlist[i], sentence)
    return sentence


def to_hour(num,unit):
    if unit == "s" or unit == "second" or unit == "seconds":
        return float(num) / float(3600)
    if unit == "min" or unit == "minute" or unit == "minutes":
        return float(num) / float(60)
    if unit == "h" or unit == "hour" or unit == "hours":
        return num
    if unit == "day" or unit == "days":
        return num*24
    if unit == "week" or unit == "weeks":
        return num * 24 * 7
    else:
        return -1


def get_time(sentence, wordlist):
    time = []
    for i in range(len(wordlist)):
        s = f"\d+\s*{wordlist[i]}[\s\.,:;'\?]"
        result = re.findall(s, sentence)
        for j in range(len(result)):
            num = re.findall("\d+", result[j])
            t = to_hour(float(str(num[0])), wordlist[i])
            if t != -1:
                time.append(t)
    return time


def main():
    wordlist = ["second", "minute", "hour", "day", "week", "s ", "min", "h", "senconds", "minutes", "hours", "days", "weeks"]
    rf = np.load("training_result.npy", allow_pickle=True)
    text_files = glob.glob(f"{ROOT}/data/papers/text/scopus/chemistry_analysis/*.txt")
    for i, text_file in enumerate(text_files):
        if i % 15 == 0:
            print(f"Searched {i / len(text_files) * 100}% of documents")
        sentences = []
        found_sentence = False
        with open(text_file, "r", encoding="utf-8") as text_paper_f:
            paper = text_paper_f.read()
            tokenizer = nltk.data.load("tokenizers/punkt/english.pickle")
            tokenized_sentences = tokenizer.tokenize(paper)

            for tokenized_sentence in tokenized_sentences:
                if ((tokenized_sentence.count(";") > 10)
                    or len(re.findall("\d+", tokenized_sentence)) > 20):
                    sentence = " "
                else:
                    sentence = re.sub(";", " ", tokenized_sentence)
                    sentence = re.sub("\s+", " ", tokenized_sentence)
            
                sentence_clean = word2num(sentence)
                time = get_time(sentence_clean, wordlist)
                if len(time) > 0:
                    print(f"{sentence}", end="\n\n")
                    rf_decision = decision(rf, tokenized_sentence)
                    if rf_decision == 1:
                        print(f"Decision = {rf_decision}")


if __name__ == "__main__":
    main()
