import os
import re
import uuid
import json
import requests

from time import sleep
from pathlib import Path

ROOT = os.getcwd().split("src")[0]


class ElsevierAPI:
    def __init__(self, api, api_key):
        self.api = api
        self.api_key = api_key
        self.url = 'https://api.elsevier.com/content/search/' + self.api
        self.download_path = f"{ROOT}/data/papers/pdf/scopus/"
        self.log_path = f"{ROOT}/src/scraping_papers/logs/scopus/"

        Path(self.download_path).mkdir(parents=True, exist_ok=True)
        Path(self.log_path).mkdir(parents=True, exist_ok=True)

    def search(self, query, count=None, start=None, stop=None):
        '''
        '''

        params = {
            'query': query
        }
        if(count): params['count'] = count
        if(start): params['start'] = start
        if(stop): params['stop'] = stop

        headers = {
                'X-ELS-APIKey': self.api_key,
                'Accept': 'application/json'
            }

        try:
            response = requests.get(
                self.url,
                params=params,
                headers=headers,
            )

            if not response.status_code == 200:
                # print('[ERROR] Response code %s' % (response.status_code))
                return 0
            
            return response

        except Exception as e:
            # print("[ERROR] Query %s\n %s" % (query, e))
            return 0

    def fetch_document(self, identifier_type, identifier, document_type, oa):
        '''
        '''

        url = 'https://api.elsevier.com/content/article'

        if identifier_type == 'pii':
            url = f"{url}/pii/{identifier}"
        elif identifier_type == 'doi':
            url = f"{url}/doi/{identifier}"
        elif identifier_type == 'scopus_id':
            url = f"{url}/scopus_id/{identifier}"
        else:
            return 0

        if oa:
            url = f"{url}?view=FULL"

        headers = {
                'X-ELS-APIKey': self.api_key
            }
        
        if document_type == 'text':
            headers['Accept'] = 'application/json'
        elif document_type == "pdf":
            headers['Accept'] = 'application/pdf'

        try:
            if document_type == "text":
                response = requests.get(
                    url,
                    headers=headers,
                )
            elif document_type == "pdf":
                response = requests.get(
                    url,
                    stream=True,
                    headers=headers,
                    timeout=30,
                )

            if not response.status_code == 200:
                print('[FETCH] Oops, an error occurred! DOI: %s \nResponse code: %s' % (url, response.status_code))
                return 0
            
            return response
        except Exception as e:
            print("[ERROR] Fetching {} {}\n {}".format(identifier_type,
                                                       identifier, e))
            return 0
    
    def download_document(self, document_id, document_type,
                          identifier_type, identifier, oa,
                          query):
        response = self.fetch_document(identifier_type, identifier,
                                       document_type, oa)
        if response == 0:
            return 0
        
        try:
            if document_type == 'text':
                response = response.json()

                if 'full-text-retrieval-response' in response.keys():
                    with open(
                        f"{self.download_path}/{document_id}.txt", 
                        'w+', 
                        encoding='utf-8'
                    ) as f:
                        if isinstance(response['full-text-retrieval-response']['originalText'], dict):
                            return 0
                        f.write(response['full-text-retrieval-response']['originalText'])
                    return 1
                else:
                    return 0
            elif document_type == 'pdf':
                with open(f"{self.download_path}/{document_id}.pdf", 'wb') as f:
                    for chunk in response.iter_content(2048):
                        f.write(chunk)
                return 1
            else:
                print("[ERROR] Please specify a document type\n")
                return 0
        except Exception as e:
            print('An error occurred: %s' % (e))
            return 0

    def abstract_retrieval(self, identifier, value):
        url = 'https://api.elsevier.com/content/abstract/'

        if identifier == 'pii':
            url = f"{url}/pii/{value}"
        elif identifier == 'doi':
            url = f"{url}/doi/{value}"
        elif identifier == 'scopus_id':
            url = f"{url}/scopus_id/{value}"
        else:
            return 0

        headers = {
                'X-ELS-APIKey': self.api_key,
                'Accept': 'application/json'
            }

        try:
            response = requests.get(
                url,
                headers=headers
            )

            if not response.status_code == 200:
                print('[ABSTRACT] Oops, an error occurred! Response code: %s' % (response.status_code))
                return 0

            return response.json()

        except Exception as e:
            print("[ERROR] Fetching abstract %s\n %s" % (url, e))
            return 0
        return 0
    
    def pull_papers(self, query,
                    worker=0, max_results=None,
                    document_type='text', oa=False):
        if document_type == "text":
            self.download_path = f"{ROOT}/data/papers/text/scopus/{query[0]}"
        elif document_type == "pdf":
            self.download_path = f"{ROOT}/data/papers/pdf/scopus/{query[0]}"

        print('[%d] Searching scopus for %s' % (worker, query[1]))

        # Check if directory exists to store downloaded files
        Path(self.download_path).mkdir(parents=True, exist_ok=True)

        start = 0
        per_search = 10
        reached_end = False 
        success = 0
        failed = 0
        if oa:
            search_query = f"{query[1]} AND ACCESSTYPE(OA)"
        else:
            search_query = f"{query[1]}"

        while not reached_end:
            # Search scopus
            result = self.search(search_query, count=per_search, start=start)
            start += per_search

            # Check search was successful
            if result == 0:
                break
                
            result = result.json()

            print('[%d] Found %d papers relevant to %s' % (worker, len(result['search-results']['entry']), query[1]))
            if(len(result['search-results']['entry'])) < per_search:
                print('[%d] Reached end of results for %s' % (worker, query[1]))
                reached_end = True

            for entry in result['search-results']['entry']:
                unique_id = str(uuid.uuid1()).replace('-', '')
                title = re.sub("[^a-zA-Z] ", "", entry['dc:title'].lower().replace('-', ' '))
                
                if "dc:identifier" in entry.keys():
                    scopus_id = entry["dc:identifier"].split(":")[1]
                    if self.download_document(unique_id, document_type, 'scopus_id', scopus_id, oa, query[1]) == 1:
                        # If successfull, find the subject area of the paper
                        subject_resp = self.abstract_retrieval("scopus_id", entry["dc:identifier"])

                        keywords = entry["authkeywords"] if "authkeywords" in entry.keys() else None

                        subject_areas = []
                        subject_areas_abbrv = []

                        if "subject-areas" in subject_resp['abstracts-retrieval-response'].keys():
                            subject_resp = subject_resp['abstracts-retrieval-response']['subject-areas']['subject-area']

                            for i, subject_area in enumerate(subject_resp):
                                subject_areas.append(subject_resp[i]['$'])
                                subject_areas_abbrv.append(subject_resp[i]['@abbrev'])
                            
                            # Replace commas in list for safe storage in CSV file
                            subject_areas = str(subject_areas).replace(',', ';')
                            subject_areas_abbrv = str(subject_areas_abbrv).replace(',', ';')
                        
                        with open(self.log_path+query[0]+'_fetch_success.csv', 'a', encoding='utf-8') as f:
                            string = (
                                f"Scopus\t{unique_id}\t{title}\t{entry['dc:identifier']}\t"
                                f"{entry['prism:doi'] if 'prism:doi' in entry.keys() else None}\t"
                                f"{entry['prism:pii'] if 'prism:pii' in entry.keys() else None}\t"
                                f"{entry['subtypeDescription']}\t{entry['citedby-count']}\t"
                                f"{entry['prism:coverDate']}\t{entry['prism:publicationName']}\t"
                                f"{keywords}\t{subject_areas}\t{subject_areas_abbrv}\n"
                            )
                            f.write(string)

                        # print('Successfully fetched text for %s' % (entry['pii']))
                        success += 1
                        continue
                    else:
                        with open(self.log_path+query[0]+'_fetch_error.csv', 'a', encoding='utf-8') as f:
                            string = (
                                f"Scopus\t{title}\t{entry['dc:identifier']}\t"
                                f"{entry['prism:doi'] if 'prism:doi' in entry.keys() else None}\t"
                                f"{entry['prism:pii'] if 'prism:pii' in entry.keys() else None}\t"
                                f"{entry['subtypeDescription']}\tFull Text\n"
                            )
                            f.write(string)
                        failed += 1

                if 'pii' in entry.keys():
                    # print('\nFetching pii %s' % (entry['pii']))
                    if self.download_document(unique_id, document_type, 'pii', entry['pii'], oa, query[0]) == 1:
                        # If successfull, find the subject area of the paper
                        subject_resp = self.abstract_retrieval('pii', entry['pii'])

                        keywords = entry["authkeywords"] if "authkeywords" in entry.keys() else None

                        subject_areas = []
                        subject_areas_abbrv = []

                        if "subject-areas" in subject_resp['abstracts-retrieval-response'].keys():
                            subject_resp = subject_resp['abstracts-retrieval-response']['subject-areas']['subject-area']

                            for i, subject_area in enumerate(subject_resp):
                                subject_areas.append(subject_resp[i]['$'])
                                subject_areas_abbrv.append(subject_resp[i]['@abbrev'])
                            
                            # Replace commas in list for safe storage in CSV file
                            subject_areas = str(subject_areas).replace(',', ';')
                            subject_areas_abbrv = str(subject_areas_abbrv).replace(',', ';')

                        # Record details of document
                        with open(self.log_path+query[0]+'_fetch_success.csv', 'a', encoding='utf-8') as f:
                            string = (
                                f"Scopus\t{unique_id}\t{title}\t{entry['dc:identifier']}\t"
                                f"{entry['prism:doi'] if 'prism:doi' in entry.keys() else None}\t"
                                f"{entry['prism:pii'] if 'prism:pii' in entry.keys() else None}\t"
                                f"{entry['subtypeDescription']}\t{entry['citedby-count']}\t"
                                f"{entry['prism:coverDate']}\t{entry['prism:publicationName']}\t"
                                f"{keywords}\t{subject_areas}\t{subject_areas_abbrv}\n"
                            )
                            f.write(string)

                        # print('Successfully fetched text for %s' % (entry['pii']))
                        success += 1
                        continue
                    else:
                        with open(self.log_path+query[0]+'_fetch_error.csv', 'a', encoding='utf-8') as f:
                            string = (
                                f"Scopus\tpii\t{title}\t{entry['prism:coverDate']}\t{entry['dc:identifier']}\t"
                                f"{entry['prism:doi'] if 'prism:doi' in entry.keys() else None}\t"
                                f"{entry['prism:pii'] if 'prism:pii' in entry.keys() else None}\t"
                                f"{entry['subtypeDescription']}\tFull Text\n"
                            )
                            f.write(string)
                        failed += 1
                        
                if 'prism:doi' in entry.keys():
                    # print('\nFetching DOI %s' % (entry['prism:doi']))
                    if self.download_document(unique_id, document_type, 'doi', entry['prism:doi'], oa, query[0]) == 1:
                        # If successfull, find the subject area of the paper
                        subject_resp = self.abstract_retrieval('doi', entry['prism:doi'])

                        keywords = entry["authkeywords"] if "authkeywords" in entry.keys() else None

                        subject_areas = []
                        subject_areas_abbrv = []

                        if "subject-areas" in subject_resp['abstracts-retrieval-response'].keys():
                            subject_resp = subject_resp['abstracts-retrieval-response']['subject-areas']['subject-area']

                            for i, subject_area in enumerate(subject_resp):
                                subject_areas.append(subject_resp[i]['$'])
                                subject_areas_abbrv.append(subject_resp[i]['@abbrev'])
                            
                            # Replace commas in list for safe storage in CSV file
                            subject_areas = str(subject_areas).replace(',', ';')
                            subject_areas_abbrv = str(subject_areas_abbrv).replace(',', ';')

                        # Record details of document
                        with open(self.log_path+query[0]+'_fetch_success.csv', 'a', encoding='utf-8') as f:
                            string = (
                                f"Scopus\t{unique_id}\t{title}\t{entry['dc:identifier']}\t"
                                f"{entry['prism:doi'] if 'prism:doi' in entry.keys() else None}\t"
                                f"{entry['prism:pii'] if 'prism:pii' in entry.keys() else None}\t"
                                f"{entry['subtypeDescription']}\t{entry['citedby-count']}\t"
                                f"{entry['prism:coverDate']}\t{entry['prism:publicationName']}\t"
                                f"{keywords}\t{subject_areas}\t{subject_areas_abbrv}\n"
                            )
                            f.write(string)

                        # print('Successfully fetched text for %s' % (entry['prism:doi']))
                        success += 1
                        continue
                    else:
                        with open(self.log_path+query[0]+'_fetch_error.csv', 'a', encoding='utf-8') as f:
                            string = (
                                f"Scopus\tdoi\t{title}\t{entry['prism:coverDate']}\t{entry['dc:identifier']}\t"
                                f"{entry['prism:doi'] if 'prism:doi' in entry.keys() else None}\t"
                                f"{entry['prism:pii'] if 'prism:pii' in entry.keys() else None}\t"
                                f"{entry['subtypeDescription']}\tFull Text\n"
                            )
                            f.write(string)
                        failed += 1
                else:
                    with open(self.log_path+query[0]+'_fetch_error.csv', 'a', encoding='utf-8') as f:
                        string = (
                            f"Scopus\t{title}\t\t{entry['dc:identifier']}\t"
                            f"{entry['prism:doi'] if 'prism:doi' in entry.keys() else None}\t"
                            f"{entry['prism:pii'] if 'prism:pii' in entry.keys() else None}\t"
                            f"{entry['subtypeDescription']}\tFull Text\n"
                        )
                        f.write(string)
                    failed += 1

                if not max_results == None and success >= max_results:
                    reached_end = True
                    break
                sleep(1)

            # print('\n\nSuccessfully downloaded %d articles' % (success))
            # print('Failed to download %d articles' % (failed))
            # print('Scraped a total of %d articles\n\n' % (success + failed))
