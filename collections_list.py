import urllib.request
import json

def get_bdr_collections():
    '''returns a dict like "'collection name':[number of items]"'''
    collection_field = 'ir_collection_name'
    solr_query = f'https://repository.library.brown.edu/api/search/?q=*&facet=on&facet.field={collection_field}&rows=0'
    query_result = urllib.request.urlopen(solr_query).read()
    facet_counts = json.loads(query_result)['facet_counts']['facet_fields'][collection_field]
    facet_iter = iter(list(facet_counts))
    result = {}

    for i in facet_iter:
        result.update({i:next(facet_iter)})

    return result 

if __name__ == '__main__':
    print( 'Dict of bdr collections: '+get_bdr_collections() )
    