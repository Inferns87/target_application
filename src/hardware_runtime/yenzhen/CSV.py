
# coding: utf-8

# In[10]:

import csv
import pandas as pd

def get_colum(Inputfile,names):
    df = pd.read_csv(Inputfile, skiprows=[0],header=None, names=names)
    List = df[colum_name].tolist()
    return List
def get_row(file_name,No):
    with open(file_name,'rb') as csvfile:
        reader = csv.reader(csvfile)
        for i,rows in enumerate(reader):
            if i == No:
                row = rows
    return row

def search_row(df,colum_name,aim):
    List=csv_get_colum(df,colum_name)
    close=difflib.get_close_matches(aim, List, n = 1,cutoff = 0.1)
    close=str(close)
    close=(close[2:len(close)-2]) #remove '[]'
    close = close.replace("\\", "")
    row=(df[df[colum_name].str.contains(close,regex=False)])
    return row

def concat_append_dataf(frame,data,dataf):
    newrow=dict(frame.items()+data.items())
    dataf = dataf.append(newrow,ignore_index=True)
    return dataf
    
def write(dataf,Outputfile):
    dataf=dataf.fillna(0) #fill na with 0
    dataf.to_csv(Outputfile)
    return 0
"""
def main():
    names=['Authors','Title','Year','Source','Volume','Issue','Art','Start','End','Count','Cited','DOI','Link','Type','Access','Database','EID']
    csv_read('scopus.csv',names)
    frame=[{'A': 0, 'B':1 , }]
    D={}
    D['C']=2
    D['D']=3
    Outputfile='test.csv'
    dataf=pd.DataFrame([])
    for i in range(10):
        dataf=append_dataf(frame,D,dataf)
    print(csv_write(dataf,Outputfile))
main()
"""

