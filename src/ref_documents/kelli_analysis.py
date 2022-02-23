import os
import re
import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Configure pdfminer
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LTTextBoxHorizontal

def read_pdf(document):
    '''
    A function to read a pdf file
    :param file        Path to the pdf file
    :param pdf_string  A string containing the pdf file
    '''

    pdf_elements = []

    # Instantiate pdf reader
    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    # Iterate through each page in the pdf file
    for page in PDFPage.get_pages(document):
        # Process the page
        interpreter.process_page(page)
        layout = device.get_result()
        for element in layout:
            if isinstance(element, LTTextBoxHorizontal):
                # Append each element to a list
                pdf_elements.append(element.get_text())

    pdf_string = ''.join(pdf_elements) # Concatenate all elements into one string
    pdf_string = ' '.join(pdf_string.split()) # Removes multiple spaces / line spaces

    return pdf_string

def main():
    submission_path = "./data/submissions/"
    search_terms = ['github', 'gitlab', 'software', 'software upgrade', 'python', 'c++', 'java']

    with open("./universities.txt", "w") as f:
        for university in os.listdir(submission_path):
            if ".DS_Store" in university:
                continue
            print('\nProcessing university {}'.format(university))
            # Iterate through the submissions made by each university
            for submission in os.listdir(submission_path + university + "/"):
                if ".DS_Store" in submission:
                    continue
                try:
                    document = open(submission_path + university + '/' + submission, 'rb')
                
                    # Read current impact submission
                    impact_submission = read_pdf(document)
                    impact_submission = impact_submission.lower()
                    for search_term in search_terms:
                        if search_term in impact_submission:
                            f.write(f"{university},{submission},{search_term}\n")
                            break                          
                except:
                    print(f"error {university},{submission}\n")
                    continue


if __name__ == "__main__":
    main()
