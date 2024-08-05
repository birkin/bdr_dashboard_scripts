"""
For reference, this was the code that gathered the pids that'll be sent to the save_mods.py script.

The goal: find all items that are orgs, but don't have an org-indicator.

So... find all items that:
- are part of the hall-hoag collection
- do not have an org-level indicator
- are not part of another item (page-scans are always part of an org-item)

Note: once the MODS are updated, this script won't yield any results.
"""

import requests

public_api_root_url = 'https://repository.library.brown.edu/api/search/'

params = {
    'q': 'rel_is_member_of_collection_ssim:"bdr:wum3gm43" AND -mods_record_info_note_hallhoagorglevelrecord_ssim:"Organization Record" AND -rel_is_part_of_ssim:*',
    'fl': 'pid,mods_id_local_ssim,primary_title',
    'start': 0,
    'rows': 500
}

api_resp: requests.Response = requests.get( public_api_root_url, params=params )

i = 0
for (i, doc) in enumerate( api_resp.json()['response']['docs'] ):
    assert type(doc) == dict
    print( doc['pid'] )
assert i + 1 == 97  # 97 items in the hall-hoag collection that are orgs, but don't have an org-level indicator
