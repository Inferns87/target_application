
# coding: utf-8

# In[ ]:


import pandas as pd
from numpy import *
import CSV
import TXT
import random
import re
import numpy as np
# from nltk.corpus import stopwords
def text_process(text):
    text=re.sub("\n", "", text)
    text=re.sub("   ", "", text)
    text=re.sub(r"[\x80-\xff]+", " ", text)
    text=re.sub("\d+","",text)
    text=re.sub("[\.,:;\'\?\"\[\]\{\}\|\(\)\\_\-/\+=]"," ",text)
    return text
def word_count(text):
    text=text.split()
    frame={}
    for i in text:
        if i not in frame:
            frame[i]=1
        if i in frame:
            frame[i]+=1
    return frame
def create_training_set(size):
    path='D:\\example\\pdf_scraper\\ALL\\'
    lis=[]
    frame={}
    dataf=pd.DataFrame([])
    wordlist=['second','minute','hour','day','week','s ','min','h','senconds','minutes','hours','days','weeks']
    searchlist1=['algorithm','calculate','calculation','simulation','iteration','code','parallel','took','takes','run','calculation','evaluation','compute','computaion','processor','desktop','computer','cluster']
    searchlist2=['cpu','cpus','ram','gpu','gpus','pc','core','cores']
    while(len(lis)<=size):
        flag=1
        while(flag):
            i=random.randint(1,10291)
            if i not in lis:
                flag=0
                lis.append(i)
    for i in lis:
        print i
        text=TXT.read(path,str(i))
        text=TXT.split_sentence(text)
        temp=[]
        for j in range(len(text)):
            if text[j].count(';')>10 or len(re.findall('\d+',text[j]))>20:
                text[j]=' '
            else:
                a=re.sub(";"," ",text[j])
                a=re.sub("\s+", " ", a)
                temp.append(a)
        text=temp
        for j in range(len(text)):
            sentence=TXT.word2num(text[j])
            if(len(TXT.get_time(sentence,wordlist))>0):
                frame['sentence']=sentence
                frame['article']=i
                frame['label']=0
                for k in searchlist1:
                    if TXT.find_word(k,sentence,1):
                        frame['label']=1
                for k in searchlist2:
                    if TXT.find_word(k,sentence,0):
                        frame['label']=1
                dataf=dataf.append(frame,ignore_index=True)
    output_CSV=path+'test_set.csv'
    CSV.write(dataf,output_CSV)
def process_training_set():
    
    frame1={}
    frame2={}
    frame3={}
    dataf1=pd.DataFrame([])
    dataf2=pd.DataFrame([])
    article=0
    frame2['sentence']=''
    frame3['sentence']=''
    for i in range(3000):
        print i+1
        row=CSV.get_row('D:\\example\\pdf_scraper\\ALL\\training_set.csv',i+1)
        frame1['label']=row[2]
        frame1['sentence']=row[3]
        dataf1=dataf1.append(frame1,ignore_index=True)
        if article==int(row[1]):
            if int(row[2])==1:
                frame2['sentence']+=row[3]
                frame2['label']=1
            else:
                frame3['sentence']+=row[3]
                frame3['label']=0
        else:
            article=int(row[1])
            if len(frame2['sentence'])>1:
                dataf2=dataf2.append(frame2,ignore_index=True)
            if len(frame3['sentence'])>1:
                dataf2=dataf2.append(frame3,ignore_index=True)
            frame2['sentence']=''
            frame3['sentence']=''
            if int(row[2])==1:
                frame2['sentence']+=row[3]
                frame2['label']=1
            else:
                frame3['sentence']+=row[3]
                frame3['label']=0
        
    CSV.write(dataf1,'D:\\example\\pdf_scraper\\ALL\\sentence_set.csv')  
    CSV.write(dataf2,'D:\\example\\pdf_scraper\\ALL\\artical_set.csv')
            
def entropy_cal(good,bad,total):
    if good==0:
        return 0
    if bad==0:
        return 0
    return -(float(good)/float(total))*math.log(float(good)/float(total),2)-(float(bad)/float(total))*math.log(float(bad)/float(total),2) 
def get_gain(size,training_set,label):
        result_tuple_list=[]
        # list_stopWords=list(set(stopwords.words('english')))
        good_total=sum(label)
        print good_total
        bad_total=size-good_total
        print bad_total
        entropy=entropy_cal(good_total,bad_total,size)
        frame={}
        corpus=[]
        good_sentences=''
        bad_sentences=''
        all_sentences=''
        for i in range(size):
            sentence=training_set[i]
            if label[i] ==0:
                bad_sentences+=sentence
            if label[i]==1:
                good_sentences+=sentence
            all_sentences+=sentence
            sentence=sentence.split()
            for j in sentence:
                if j not in corpus and len(j)>1:
                    corpus.append(j)
        good_count=word_count(good_sentences)
        bad_count=word_count(bad_sentences)
        all_count=word_count(all_sentences)
        skipped=0
        for i in corpus:
            if i in good_count:
                g=good_count[i]
            else:
                g=0
            if i in bad_count:
                b=bad_count[i]
            else:
                b=0
            a=all_count[i]
            entropy_word=entropy_cal(g,b,a)
            gain=entropy-entropy_word
            l=re.findall('[a-z]+',i)
            if g>=b:
                weight=float(g)/float(good_total)
                l=1
            else:
                weight=float(b)/float(bad_total)
                l=0
            result_tuple_list.append([i,gain,weight,l])

            
        result_tuple_list.sort(key= lambda k:k[1],reverse=True)
        return result_tuple_list
def decision(tree,sentence):
    sentence=sentence.split()
    for i in tree:
        if i[0] in sentence and i[1]==1:
            return 1
    return 0
def vote(sentence,forest):
    sentence=text_process(sentence)
    count=0
    for i in range(len(forest)):
        count+=decision(forest[i],sentence)
    if count>float(len(forest))*0.2:
        return 1
    else:
        return 0
class random_forest:
    def __init__ (self,m,training_set_size, tree_num,sentence_set_csv):
        self.m=m
        self.size=training_set_size
        self.tree_num=tree_num
        self.sentence_set=sentence_set_csv
        self.sentence=[]
        self.label=[]
        for i in range(self.size):
            row=CSV.get_row(self.sentence_set,i+1)
            self.sentence.append(text_process(row[2]))
            self.label.append(int(row[1]))
    
    def bagging(self):
        bag_list=[]
        oob=[]
        for i in range(self.size):
            r=random.randint(0,self.size-1)
            bag_list.append(r)
        for i in range(self.size):
            if i not in bag_list:
                oob.append(i)
        return bag_list,oob
    
    def create_tree(self):
        bag_list,oob=self.bagging()
        tree=[]
        label=[]
        sentence=[]
        for i in bag_list:
            sentence.append(self.sentence[i])
            label.append(self.label[i])
        flag=1
        while(flag):
            gain=get_gain(len(sentence),sentence,label)
            best_features=[]
            stop=1
            count=0
            before=gain[0][1]
            while(stop):
                ga=gain[count][1]
                if ga == before and count<=(len(gain)-1):
                    best_features.append(gain[count])
                else:
                    stop=0
                count+=1
            best_features.sort(key= lambda k:k[2],reverse=True)
            node=best_features[0]
            tree.append([node[0],node[3]])
            stop=1
            count=0
            while(stop):
                s=sentence[count].split()
                if node[0] in s:
                    del sentence[count]
                    del label[count]
                else:
                    count+=1
                if count==len(sentence):
                    stop=0
            if sum(label)==len(label) or sum(label)==0:
                flag=0
        print tree
        correct=0
        no_decision=0
        for i in oob:
            d=decision(tree,self.sentence[i])
            if d==self.label[i]:
                correct+=1
            if d==0.5:
                no_decision+=1
            
        oob_accuracy=float(correct)/float(len(oob)-no_decision)
            
        return tree,oob_accuracy
    def create_forest(self):
        self.create_tree()
        ooba_total=0
        forest=[]
        for i in range(self.tree_num):
            tree,oob_accuracy=self.create_tree()
            forest.append(tree)
            ooba_total+=oob_accuracy
        ooba_average=ooba_total/float(self.tree_num)
        print('the average out of bag accuracy is:'+str(ooba_average))
        return forest



        
                
            
                
        
        
if __name__=='__main__':
    r=random_forest(1000,3000,100,'D:\\example\\pdf_scraper\\ALL\\sentence_set.csv')
    forest=r.create_forest()
    np.save("training_result.npy",forest)
    print "traning result saved"
    forest=np.load("training_result.npy")
    '''   
    
    saved_matrix = np.loadtxt(open("train_result.csv","rb"),delimiter=",",skiprows=0)
    print saved_matrix
    for i in range(len(r.sentence)):
        print(vote(r.sentence[i],saved_matrix))
        print(r.label[i])
        print "###"
    '''




        

