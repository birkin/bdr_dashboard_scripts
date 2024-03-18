"""
Getting the 85 items that are "part-of" the Time-Magazine org in the Hall-Hoag collection...
- tried the api version of the display facet-url, which does NOT work: 
    - display: <https://repository.library.brown.edu/studio/collections/bdr:wum3gm43/?selected_facets=subject%3ATime+Magazine%2C+Inc.>
    - api: <https://repository.library.brown.edu/api/collections/bdr:wum3gm43/?selected_facets=subject%3ATime+Magazine%2C+Inc.>
- looked at the first page-0001 item in the api.
    - item: <https://repository.library.brown.edu/studio/item/bdr:d7cc58f6/>
    - api: <https://repository.library.brown.edu/api/items/bdr:d7cc58f6/>
- saw the `"rel_is_part_of_ssim": ["bdr:9x6r2xgj"]` key-val.
- confirmed that this pid is for the Time Magazine org: <https://repository.library.brown.edu/studio/item/bdr:9x6r2xgj/>
- used the search-api to get the items: <https://repository.library.brown.edu/api/search/?q=rel_is_part_of_ssim:bdr:9x6r2xgj&rows=100>
- update: add the `&fl=pid,identifier` to the search-api url to get only the pid and identifier fields:
  <https://repository.library.brown.edu/api/search/?q=rel_is_part_of_ssim:bdr:9x6r2xgj&rows=100&fl=pid,identifier>
"""

import json

data: dict = json.loads( open('./the_85.json').read() )
print( f'keys, {data.keys()}' )

docs: list = data['response']['docs']
print( f'len(docs), {len(docs)}' )

## works, but I want the items sorted by their identifer, eg 'HH001545_0001', then 'HH001545_0002', etc
# pids: list = [ doc['pid'] for doc in docs ]
# print( f'len(pids), {len(pids)}' )
# print( f'pids, {pids[:5]}' )

## get list of tuples of (pid, identifier)
pids_and_identifiers: list = [ (doc['pid'], doc['identifier'][0]) for doc in docs ]
print( f'- len(pids_and_identifiers), {len(pids_and_identifiers)}' )
print( f'- pids_and_identifiers (first few), {pids_and_identifiers[:5]}...' )

## sort on identifier
pids_and_identifiers.sort( key=lambda x: x[1] )
print( f'- pids_and_identifiers after sort (first few), {pids_and_identifiers[:5]}...' )

## list of pids
pids: list = [ x[0] for x in pids_and_identifiers ]
print( f'- len(pids), {len(pids)}' )
print( f'- pids (first few), {pids[:5]}...' )

## write to file
jsn = json.dumps( pids, indent=2 )
with open( './pid_list.json', 'w' ) as f:
    f.write( jsn )
