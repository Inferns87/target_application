
# coding: utf-8

# In[6]:



import sys
import re
import csv
import matplotlib.pyplot as plt
import numpy as np
# import nltk
# import nltk.data
def find_word(word,text,flag):
    if flag==1:
        if word in text:
            return 1
        else:
            return 0
    if flag==0:
        if len(re.findall(' '+word+' ',text))>0:
            return 1
        else:
            return 0
# def split_sentence(text):
#     tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
#     sentences = tokenizer.tokenize(text)
#     return sentences


def read(path,file_name):
    f=open(path+file_name+'.txt')
    text=''
    for line in f:
        text+=line
    f.close()
    return text
def write(path,title,text):
    path=path+title+'.txt'
    f1 = open(path,'a')
    f1.write(text)
    f1.close
    
def to_hour(num,unit):
    if unit=='s' or unit=='second' or unit=='seconds':
        return float(num)/float(3600)
    if unit=='min' or unit =='minute' or unit=='minutes':
        return float(num)/float(60)
#if(unit.count('h')-unit.count('month')):
    if unit=='h' or unit=='hour' or unit=='hours':
        return num
    if unit=='day' or unit =='days':
        return num*24
    if unit == 'week' or unit == 'weeks':
        return num*24*7
    else:
        return -1
    
def get_time(sentence,wordlist):
    time=[]
    for i in range(len(wordlist)):
        s='\d+\s*'+wordlist[i]+'[\s\.,:;\'\?]'
        result=re.findall(s,sentence)
        for j in range(len(result)):
            num=re.findall('\d+',result[j])
            t=to_hour(float(str(num[0])),wordlist[i])
            if t!=-1:
                time.append(t)
    return time
def get_time_no_space(sentence,wordlist):
    time=[]
    for i in range(len(wordlist)):
        s='\d+'+wordlist[i]+'[\s\.,:;\'\?]'
        result=re.findall(s,sentence)
        for j in range(len(result)):
            num=re.findall('\d+',result[j])
            t=to_hour(float(str(num[0])),wordlist[i])
            if t!=-1:
                time.append(t)
    return time
def word2num(sentence):
    wordlist=['one','two','three','four','five', 'six','seven','nine','ten','several']
    numlist=['1','2','3','4','5','6','7','8','9','10','3']
    for i in range(len(wordlist)):
        sentence=re.sub(wordlist[i],numlist[i],sentence)
    return sentence