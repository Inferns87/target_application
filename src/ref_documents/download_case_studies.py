from bs4 import BeautifulSoup
from urllib.request import urlopen
from io import BytesIO
from zipfile import ZipFile
import requests
import os
import re

def fetch_links(url):
    '''
    https://pythonspot.com/extract-links-from-webpage-beautifulsoup/
    '''

    url = urlopen(url)
    soup = BeautifulSoup(url, features="html.parser")
    links = []

    for link in soup.findAll('a', attrs={'href': re.compile("^/")}):
        links.append(link.get('href'))

    return links

url = 'https://results.ref.ac.uk/(S(ur021fkijjh1i50lcu4n4z5s))/DownloadSubmissions/SelectHei'
links = fetch_links(url) # Fetch links on page

# Iterate through each link and download all zip files
for link in links:
    # Check we have a valid download link
    if not '/DownloadSubmissions/ByHei' in link:
        continue

    print("[START] Processing %s" % (link))

    link = link.split('/DownloadSubmissions/ByHei/')
    download_id = link[0]
    institution_id = link[1]

    # Fetch University Name
    link = 'https://results.ref.ac.uk/(S(un1mxnzzwyu5dna25q5nlvbu))/DownloadSubmissions/ByHei/' + institution_id
    html = requests.get(link).text
    soup = BeautifulSoup(html, features="html.parser")
    res = soup.findAll("h2")
    university_name = None

    for r in res:
        university_name = r.text

    # Download zip file
    zip_url = 'https://results.ref.ac.uk/' + download_id + '/DownloadFile/Institution/' + institution_id + '/excel'
    zip_file = requests.get(zip_url)
    zip_file = ZipFile(BytesIO(zip_file.content))

    # Check if path already exists
    if os.path.isdir('./data/submissions/' + university_name.replace(' ', '')):
        with open('logs/submission_download_warning.csv', 'a') as f:
            f.write('{}, {}\n'.format(university_name.replace(' ', ''), e))
        continue

    # Unzip file to data directory
    try:
        zip_file.extractall('./data/submissions/' + university_name.replace(' ', ''))
    except Exception as e:
        with open('logs/submission_download_fail.csv', 'a') as f:
            f.write('{}, {}\n'.format(university_name.replace(' ', ''), e))

    print("[SUCCESS] Finished processing %s (%s)" % (university_name, link))