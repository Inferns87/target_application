import os
import json
import uuid
import requests
import xmltodict
import feedparser

from time import sleep

class ArxivAPI():
    def __init__(self):
        self.api_url = "http://export.arxiv.org/api/query"

        self.download_path = './papers/arxiv/'
        self.log_path = './logs/arxiv/'

        # Check if directory exists to store papers
        if not os.path.isdir(self.download_path):
            os.makedirs(self.download_path)

        # Check if directory exists to store logs
        if not os.path.isdir(self.log_path):
            os.makedirs(self.log_path)
    
    def search(self, query, count=None, start=None, stop=None):
        params = {
            'search_query': query
        }

        if count is not None: params['max_results'] = count
        if start is not None: params['start'] = start

        headers = {
            'Accept': 'application/json'
        }

        try:
            response = requests.get(
                self.api_url,
                params=params,
                headers=headers,
            )

            if not response.status_code == 200:
                # print('[ERROR] Response code %s' % (response.status_code))
                return 0
            
            return response

        except Exception as e:
            print("Error when searching for query %s:\n%s" % (query, e))

        return 0

    def pull_papers(self, query, worker=0, max_results=None):
        print('[%d] Searching ArXiV for %s' % (worker, query))

        download_path = './papers/arxiv/' + query

        # Check if directory exists to store downloaded files
        if not os.path.isdir(download_path):
            os.mkdir(download_path)

        reached_end = False
        start = 0
        per_search = 10
        success = 0
        failed = 0
        
        while not reached_end:
            result = self.search(query, count=per_search, start=start)
            n_pulled = 0
            if result == 0:
                break
            
            result = xmltodict.parse(result.text)['feed']

            try:
                for entry in result['entry']:
                    # Generate unique id
                    unique_id = str(uuid.uuid1()).replace('-', '')
                    
                    # Pull paper from ArXiV
                    response = requests.get(entry['link'][1]['@href'])

                    if response.status_code == 200:
                        open('./papers/arxiv/%s/%s.pdf' % (query, unique_id), 'wb').write(response.content)
                    
                        # Save to success log
                        with open('./logs/arxiv/'+query+'_fetch_success.csv', 'a', encoding='utf-8') as f:
                            f.write("%s\t%s\t%s\t%s\t%s\n" % (
                                    'Arxiv',
                                    unique_id,
                                    entry['title'].replace('\n', ''),
                                    entry['arxiv:primary_category']['@term'],
                                    # entry['category'],
                                    entry['id']
                                ))
                        success += 1
                    else:
                        with open('./logs/arxiv/'+query+'_fetch_error.csv', 'a', encoding='utf-8') as f:
                            f.write("%s\t%s\t%s\t%s\t%s\n" % (
                                    'Arxiv',
                                    unique_id,
                                    entry['title'],
                                    entry['arxiv:primary_category']['@term'],
                                    # entry['category'],
                                    entry['id']
                                ))
                        failed += 1
                    n_pulled += 1
                    sleep(2)
            except Exception as e:
                print("An error occurred:\n{}".format(e))
                sleep(60)
                pass

            sleep(2)
            start += n_pulled
                
            if max_results is not None and success >= max_results:
                reached_end = True
                break

            print("----- Worker {} -----".format(worker))
            print('Successfully downloaded %d articles' % (success))
            print('Failed to download %d articles' % (failed))
            print('Scraped a total of %d articles\n\n' % (success + failed))