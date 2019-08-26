from Bio import Entrez
import json

def search(query):
    Entrez.email = 'your.email@example.com'
    handle = Entrez.esearch(db='pubmed', 
                            sort='relevance', 
                            retmax='20',
                            retmode='xml', 
                            term=query)
    results = Entrez.read(handle)
    return results

def fetch_details(id_list):
    ids = ','.join(id_list)
    Entrez.email = 'your.email@example.com'
    handle = Entrez.efetch(db='pubmed',
                           retmode='xml',
                           id=ids)
    results = Entrez.read(handle)
    return results

if __name__ == '__main__':
    results = search('fever')
    id_list = results['IdList']
    papers = fetch_details(id_list)
    for i, paper in enumerate(papers['PubmedArticle']): 
        print("%d) %s" % (i+1, paper['MedlineCitation']['Article']['ArticleTitle']))
        try:
            print(paper['MedlineCitation']['Article']['Abstract']['AbstractText'][0])
        except Exception as e:
            print("No Abstract")
    # Pretty print the first paper in full
    #import json
#print(json.dumps(papers[0], indent=2, separators=(',', ':')))