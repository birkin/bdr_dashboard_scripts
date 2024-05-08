import json, pathlib
import requests

def update_hhoag_orgs():
    """ Manager.
        Called by dundermain. """
    orgs_map: dict = get_or_make_orgs_map()
    # orgs_filepath: pathlib.Path = get_or_make_orgs_file()
    print('done')


def get_or_make_orgs_map() -> dict:
    """ Get orgs_map.
        Looks like: {
            'HH001645': {'pid': 'bdr:x6nmpxth', 'title': 'Torch records'},
            etc.
            } 
        """
    orgs_dict = {}
    possible_path = pathlib.Path( '../../support_stuff/update_hhoag_orgs/orgsmap.json' )
    if possible_path.exists():
        orgs_dict: dict = json.load( possible_path.open() )
    else:
        url = 'https://repository.library.brown.edu/api/search/?q=-rel_is_part_of_ssim:*+rel_is_member_of_collection_ssim:"bdr:wum3gm43"&fl=pid,identifier,primary_title'
        jdict: dict = requests.get(url).json()
        for doc in jdict['response']['docs']:
            pid = doc['pid']
            identifier = doc['identifier']
            title = doc['primary_title']
            orgs_dict[identifier] = {'pid': pid, 'title': title}
    print( 'initial orgs_dict, ``{orgs_dict}``' )
    ## convert dict to sorted dict and sort keys
    sorted_orgs_dict = dict(sorted(orgs_dict.items()))
    print( 'sorted_orgs_dict, ``{sorted_orgs_dict}``')
    ## save to json file
    with open(possible_path, 'w') as f:
        jsn = json.dumps( sorted_orgs_dict, sort_keys=True, indent=2 )
        f.write( jsn )
    return sorted_orgs_dict



## dundermain
if __name__ == '__main__':
    update_hhoag_orgs()