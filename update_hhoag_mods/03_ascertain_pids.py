"""
- See if the local `data_files/03_pids_from_api.json` exists; if not, create it.
- Load the local `data_files/03_pids_from_api.json` file. 
- Load the local `update_hhoag_orgs_support_stuff/02b_hhoag_mods_paths.json` file. This will be the dict that'll be updated.
- Loop through the api-json file, and for each entry:
    - Parse the hall-hoag-id
    - Get the pid
    - Add the pid to the paths-dict.
- Save the updated paths-dict to a new json file, `update_hhoag_orgs_support_stuff/03_paths_and_pids.json`.
"""

import time, json, os, pathlib, pprint, logging
import requests


## setup logging ----------------------------------------------------
lglvl: str = os.environ.get( 'HHDICT__LOGLEVEL', 'DEBUG' )
lglvldct = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO }
logging.basicConfig(
    level=lglvldct[lglvl],  # assigns the level-object to the level-key loaded from the envar
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger( __name__ )


## manager ----------------------------------------------------------
def manage_add_pids_to_paths():
    """ Manages adding pids to paths-dict.
        Called by dundermain. """
    pids_from_api: dict = load_pids_from_api()
    pass


## helpers ----------------------------------------------------------
def load_pids_from_api() -> dict:
    """ Loads pids from api-json file.
        If it doesn't exist, creates it.
        Called by manage_add_pids_to_paths() 
        NOTE: """
    pids_from_api_filepath = pathlib.Path( './update_hhoag_mods/data_files/03_pids_from_api.json' )
    if not pids_from_api_filepath.exists():
        url = 'https://repository.library.brown.edu/api/search/?q=mods_id_local_ssim:*HH007174*&fl=mods_id_bdr_pid_ssim,primary_title,pid&rows=500'
        pids_from_api = {}
        with open( pids_from_api_filepath, 'w' ) as f:
            f.write( '{}' )
    else:
        with open( pids_from_api_filepath, 'r' ) as f:
            pids_from_api = json.loads( f.read() )
    log.debug( f'pids_from_api, partial, ``{pprint.pformat(pids_from_api)[0:500]}...``' )
    return pids_from_api


## dunndermain ------------------------------------------------------
if __name__ == '__main__':
    assert pathlib.Path.cwd().name == 'bdr_scripts_public', f"Error: wrong directory; cd to the `bdr_sripts_public` directory and try again."
    start_time = time.monotonic()
    manage_add_pids_to_paths( )
    elapsed_time = time.monotonic() - start_time
    log.info( f'elapsed time, ``{elapsed_time:.2f}`` seconds' )
