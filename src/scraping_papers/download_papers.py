import os
import time
import threading
from API.ElsevierAPI import ElsevierAPI
from API.ArxivAPI import ArxivAPI


scopus = ElsevierAPI('scopus', '37f98aeed1223d61de40968122ab95bc')
arxiv  = ArxivAPI()


N_THREADS = 4
N_PAPERS  = 2000
DEBUG = True
DATABASE = 'scopus'


SEARCH_TERMS = [
    # "TITLE-ABS-KEY(\"MCMC\")",
    # "TITLE-ABS-KEY(\"Metropolis Hasting\")",
    # "TITLE-ABS-KEY(\"Simulated Annealing\")",
    # "TITLE-ABS-KEY(\"Slice Sampling\")",
    # "TITLE-ABS-KEY(\"Gibbs Sampling\")",
    # "TITLE-ABS-KEY(\"Expectation Maximization\")",

    # ("chemistry_analysis",
    # "\"medicinal chemistry\" ALL ( ( brms AND bürkner ) OR ( gelman AND hoffman AND stan ) OR mc-stan.org OR rstanarm OR pystan OR ( rstan AND NOT mit ))")

    # ("epsrc_analysis_q1",
    #  "FUND-SPONSOR (\"Engineering and Physical Sciences Research Council\")  AND  ALL ( ( brms  AND  bürkner )  OR  ( gelman  AND  hoffman  AND  stan )  OR  mc-stan.org  OR  rstanarm  OR  pystan  OR  ( rstan  AND NOT  mit ) )")

    ("epsrc_analysis_q2",
     "FUND-SPONSOR (\"Engineering and Physical Sciences Research Council\") AND ALL (\"Markov Chain Monte Carlo\" OR MCMC OR \"Metropolis Hastings\" OR \"No U-Turn Sampler\" OR (NUTS AND (hoffman OR gelman)))")
]


def search(worker, database, terms, n_papers, oa=False):
    for term in terms:
        if database == 'scopus':
            print('--- Worker {} pulling papers from Scopus ---'.format(worker))
            scopus.pull_papers(term, worker, n_papers, "text", oa=oa)
        elif database == 'arxiv':
            print('--- Worker {} pulling papers from ArXiV ---'.format(worker))
            arxiv.pull_papers(term, worker, n_papers)
        else:
            break


if __name__ == '__main__':
    if DEBUG:
        print('[DEBUG] Pulling {} papers from {}'.format(N_PAPERS, DATABASE, N_THREADS))
        search(0, DATABASE, SEARCH_TERMS, N_PAPERS)
    else:
        print('Pulling {} papers from {} using {} threads'.format(N_PAPERS, DATABASE, N_THREADS))
        if N_THREADS < 1: N_THREADS = 1
        split_terms = [[] for i in range(N_THREADS)]
        j = 0
        for search_term in SEARCH_TERMS:
            if j >= N_THREADS: j = 0
            split_terms[j].append(search_term)
            j += 1

        try:
            threads = []
            for i in range(N_THREADS):
                threads.append(threading.Thread(target=search, args=(i, DATABASE, split_terms[i], N_PAPERS)))
            for thread in threads:
                thread.setDaemon(True)
                thread.start()
                time.sleep(2)
            main_thread = threading.currentThread()
            for t in threading.enumerate():
                if t is main_thread:
                    continue
                t.join()
        except (KeyboardInterrupt, SystemExit):
            print('\n\nReceived keyboard interrupt, quitting threads.')
