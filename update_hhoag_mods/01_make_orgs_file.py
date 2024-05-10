"""
Creates text-file of existig 97 orgs. 
Purpose: to pass that file to the pipeline's make_mods_dir.py file to reproduce all the MODS files.
Usage: python ./update_hhoag_mods/01_make_orgs_file.py
NOTE: script will need to be tweaked to to, say, get all the orgs once there are more. 
"""

import json, pathlib
import requests


def make_orgs_file() -> None:
    orgs = []
    url = 'https://repository.library.brown.edu/api/search/?q=-rel_is_part_of_ssim:*+rel_is_member_of_collection_ssim:"bdr:wum3gm43"&fl=pid,identifier,primary_title&rows=100'
    jdict: dict = requests.get(url).json()
    for entry in jdict['response']['docs']:
        orgs.append( entry['identifier'][0] )  # 'identifier' is a single-element list
    orgs.sort()
    with open('./update_hhoag_mods/data_files/01_orgs.txt', 'w') as f:
        for org in orgs:
            f.write( org + '\n' )
    return


if __name__ == '__main__':
    assert pathlib.Path.cwd().name == 'bdr_scripts_public', f"Error: wrong directory; cd to the `bdr_sripts_public` directory and try again."
    make_orgs_file()