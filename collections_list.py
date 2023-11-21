import urllib.request
import json
from columnar import columnar

def get_bdr_collections():
    '''returns a dict like "'collection name':[number of items]"'''

    collection_field = 'ir_collection_name' #field to facet on
    bdr_api = 'https://repository.library.brown.edu/api/search/'
    solr_query = f'?q=*&facet=on&facet.field={collection_field}&rows=0'
    query_result = urllib.request.urlopen(bdr_api + solr_query).read()
    facet_counts = json.loads(query_result)['facet_counts']['facet_fields'][collection_field] #drill down to list
    
    #facet_counts is a list like ['collection name',number of items,'collection name',number of items, ...]
    #so, make dict like {facet_counts[0]:facet_counts[1],facet_counts[2]:facet_counts[3], ...]
    facet_iter = iter(list(facet_counts))
    result = {i:next(facet_iter) for i in facet_iter}

    return result 

if __name__ == '__main__':
    #use columnar to make printout show columns
    bdr_collections = get_bdr_collections()
    collection_table = [[key,value] for key,value in bdr_collections.items()]
    print(columnar(collection_table,headers=['collection', 'no. items'],no_borders=True))
    print(f'Total number of collections: {len(bdr_collections)}')