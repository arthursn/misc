# -*- coding: utf-8 -*-

import sys

import requests
# Python library for pulling data out of HTML and XML files
from bs4 import BeautifulSoup


def doi2bib(doi, timeout=5.):
    """
    Return a bibTeX string of metadata for a given DOI.
    https://gist.github.com/jrsmith3/5513926
    """
    url = 'http://dx.doi.org/' + doi
    headers = {'accept': 'application/x-bibtex'}
    r = requests.get(url, headers=headers, timeout=timeout)
    if r.status_code == 200:
        return r.text


def scrape_thesis(url):
    """
    Scrape thesis from url
    """
    meta = {}
    DCmeta = {}
    r = requests.get(url)
    if r.status_code == 200:  # success!
        soup = BeautifulSoup(r.content, 'html.parser')
        for field in soup.find('head').find_all('meta'):
            lang = field.get('xml:lang')
            name = field.get('name')
            content = field.get('content')

            if lang:
                if lang not in DCmeta.keys():
                    DCmeta[lang] = {}

                if name in DCmeta[lang].keys():
                    DCmeta[lang][name].append(content)
                else:
                    DCmeta[lang][name] = [content]
            else:
                if name in meta.keys():
                    meta[name].append(content)
                else:
                    meta[name] = [content]
    return meta, DCmeta


def data2csv(thesis_data):
    csv = []
    for entry in thesis_data:
        entry = ['\''+s+'\'' if s else '' for s in entry]
        csv.append(';'.join(entry))
    return 'name;title;area;document;faculty;year;url;doi\n' + '\n'.join(csv)


f = open('teses_pmt.csv', 'w')

url = 'http://www.teses.usp.br/teses/disponiveis/3/3133/'
query = ''
r = requests.get(url + query)
j = 0
s = 'index;author;title\n'
f.write(s)
if r.status_code == 200:
    soup = BeautifulSoup(r.content, 'html.parser')
    for a in soup.find_all('a'):
        href = a.get('href')
        if href[:3] == 'tde':
            j += 1
            meta, DCmeta = scrape_thesis(url + href)
            s = '{:d};"{:}";"{:}"\n'.format(
                j, meta['citation_author'][0], meta['citation_title'][0])
            sys.stdout.write(s)
            f.write(s)
f.close()


# fnameout = 'teses_ltf.csv'
# thesis_data = scrape_teses_usp('http://www.teses.usp.br/index.php?option=com_jumi&fileid=14&Itemid=161&id=E7A0B2A3748E&lang=pt-br')  # Teses orientadas pelo Hélio

# fnameout = 'teses_pmt.csv'
# thesis_data = scrape_teses_usp('http://www.teses.usp.br/index.php?option=com_jumi&fileid=9&Itemid=159&lang=en&id=3133&prog=3008')  # Metallurgical and Materials Engineering

# fout = open(fnameout, 'w')
# fout.write(data2csv(thesis_data))
# fout.close()

# fout = open('teses_ltf.bib', 'w')

# for url, doi in thesis_data:
#     if doi:
#         bibtex = doi2bib(doi)
#         if bibtex:
#             print('Processing DOI {}'.format(doi))
#             fout.write(bibtex)
#             fout.write('\n\n')
#             fout.flush()
#         else:
#             print('DOI {} not found'.format(doi))

# fout.close()
