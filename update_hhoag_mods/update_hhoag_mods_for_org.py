"""
Updates all org-mods and item-mods for given orgs.
Checks and updates tracker files.

Example usage:
- minimum required:
    $ python ./update_hhoag_mods.py --org_list "fooA,fooB" --mods_dir "bar" --tracker_dir "baz" 
- to check envars and quit:
    $ python ./update_hhoag_mods.py --org_list "fooA,fooB" --mods_dir "bar" --tracker_dir "baz" --check_envars "True"

Note that some of the functions contain doctests. All doctests can be run with the following command:
`python -m doctest ./update_hhoag_mods/update_hhoag_mods_for_org.py -v`

Optional TODOs:
- Move the mods-dir-path and tracker-dir-path to envars. Makes more sense for CLI args to be things that change.

Code structure:
- dundermain at bottom.
- manager function at just above it.
- helper functions start at top in order of use.
"""

import argparse, collections, json, logging, os, pathlib, pprint, subprocess, sys, time
import requests
from dotenv import load_dotenv, find_dotenv


## load envars -----------------------------------------------------
load_dotenv( find_dotenv(raise_error_if_not_found=True) )
BDR_API_ROOT: str = os.environ[ 'UHHM__BDR_API_URL_ROOT' ]  # UHHM for "update hall-hoag mods"
LGLVL: str = os.environ.get( 'UHHM__LOGLEVEL', 'DEBUG' )
BINARY_PATH: str = os.environ[ 'UHHM__UPDATE_MODS_BINARY_PATH' ]
## for the `update_mods` python-binary (UM) ##
BINARY_API_AGENT: str = os.environ[ 'UM__API_AGENT' ]
BINARY_API_IDENTITY: str = os.environ[ 'UM__API_IDENTITY' ]
BINARY_API_ROOT_URL: str = os.environ[ 'UM__API_ROOT_URL' ]
BINARY_LOGLEVEL: str = os.environ.get( 'UM__LOGLEVEL', 'INFO' )
BINARY_MESSAGE: str = os.environ[ 'UM__MESSAGE' ]

## setup logging ----------------------------------------------------
lglvldct = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO }
logging.basicConfig(
    level=lglvldct[LGLVL],  # assigns the level-object to the level-key loaded from the envar
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger( __name__ )


## helpers start (manager function is after helpers) ----------------

def config_parser() -> argparse.ArgumentParser:
    """ Configures parser.
        Called by dundermain. """
    parser = argparse.ArgumentParser(description='Recursively finds JSON files in specified directory.')
    parser.add_argument( '--org_list', required=True, help='takes orgs to process; example "HH123456" or "HH123456,HH654321"' )
    parser.add_argument( '--mods_dir', required=True, help='takes path to directory containing pre-made org-mods and item-mods files' )
    parser.add_argument( '--tracker_dir', required=True, help='takes path to directory containing the tracker files' )
    parser.add_argument( '--check_envars', required=False, help='if "True", checks envars and exits' )
    return parser


def validate_arg_paths( mods_directory_path: pathlib.Path, tracker_directory_path: pathlib.Path ) -> None:
    """ Validates argument paths.
        Called by dundermain. """
    if not mods_directory_path.exists():
        print( f'Error: The path {mods_directory_path} does not exist.', file=sys.stderr )
        sys.exit(1)
    if not tracker_directory_path.is_dir():
        print( f'Error: The path {tracker_directory_path} is not a directory.', file=sys.stderr )
        sys.exit(1)
    return


def display_envars() -> None:
    """ Displays envars.
        Called by dundermain. """
    print( f'''

Envars:
          
For this `update_hhoag_mods_for_org.py` script...
- BDR_API_ROOT, ``{BDR_API_ROOT}``          
- LGLVL, ``{LGLVL}``

For the `update_mods_python_binary` file...
- BINARY_PATH, ``{BINARY_PATH}``
- BINARY_API_AGENT, ``{BINARY_API_AGENT}``
- BINARY_API_IDENTITY, ``{BINARY_API_IDENTITY}``
- BINARY_API_ROOT_URL, ``{BINARY_API_ROOT_URL}``
- BINARY_LOGLEVEL, ``{BINARY_LOGLEVEL}``
- BINARY_MESSAGE, ``{BINARY_MESSAGE}``

(end)
''')
    sys.exit( 0 )
    return


def get_org_tracker_filepath( org: str, tracker_directory_path: pathlib.Path ) -> pathlib.Path:
    """ Gets the org's tracker file path.
        Called by manage_org_mods_update(). 
    Doctest:
    >>> get_org_tracker_filepath( 'HH123456', pathlib.Path('/path/to/foo') )    
    PosixPath('/path/to/foo/HH12/3456/HH123456__whole_org_updated.json')
    """
    part_a, part_b = org[:4], org[4:8]
    org_tracker_filepath = tracker_directory_path / part_a / part_b / f'{org}__whole_org_updated.json'  # pathlib way of joining paths
    log.debug(f'org_tracker_filepath, ``{org_tracker_filepath}``')
    return org_tracker_filepath


def check_tracker( tracker_filepath: pathlib.Path ) -> bool:
    """ Checks if org or item is already in tracker file.
        Called by manage_org_mods_update(). """
    return_val = False
    if tracker_filepath.exists():
        return_val = True
    log.debug( f'return_val `{return_val}`' )
    return return_val


def get_filepath_data( org: str, mods_directory_path: pathlib.Path ) -> dict:
    """ Creates initial org-data dict and populates it with filepath info.
        Called by manage_org_mods_update(). """
    # log.info( f'mods_directory_path, ``{mods_directory_path}``' )
    org_data = {}
    mods_paths = list( mods_directory_path.rglob('*mods.xml') )
    org_data = {}
    for mods_filepath in mods_paths:
        if org in mods_filepath.name:
            # item_dict = { 'path': str(mods_filepath) }
            item_dict = { 'path': mods_filepath }
            hh_id: str = parse_id( mods_filepath )
            org_data[ hh_id ] = item_dict
    sorted_org_data = collections.OrderedDict( sorted(org_data.items()) )  # doesn't _need_ to be sorted, but it makes debugging a bit easier
    log.debug( f'org_data, partial, ``{pprint.pformat(sorted_org_data)[0:1000]}...``' )
    return sorted_org_data


def parse_id( mods_file: pathlib.Path ) -> str:
    """ Returns hall-hoag-id from mods-filepath.
        Called by get_filepath_data() 
    >>> mods_filepath = pathlib.Path( '/path/to/HH123456.mods.xml' )  # org
    >>> parse_id( mods_filepath )
    'HH123456'
    >>> mods_filepath = pathlib.Path( '/path/to/HH123456_0001.mods.xml' )  # item
    >>> parse_id( mods_filepath )
    'HH123456_0001'
    """
    filename_a: str = mods_file.stem  # removes .xml but still contains .mods
    filename_b: str = filename_a.split('.')[0]  # removes .mods    
    return filename_b


def get_org_data_via_api( org: str ) -> list:
    """ Gets org data via BDR public API.
        Called by manage_org_mods_update(). """
    api_data = []
    start = 0
    rows = 500
    org_data_url_stable_pattern = f'{BDR_API_ROOT}/search/?q=mods_id_local_ssim:*{org}*&fl=mods_id_local_ssim,primary_title,pid&rows={rows}'
    log.debug( f'org_data_url_stable_pattern, ``{org_data_url_stable_pattern}``' )
    while True:
        org_data_url = f'{org_data_url_stable_pattern}&start={start}'
        log.debug( f'org_data_url, ``{org_data_url}``' )
        response = requests.get(org_data_url)
        response_data = response.json()
        docs: list = response_data['response']['docs']   
        api_data.extend( docs )            
        if len( response_data['response']['docs'] ) < rows:  # means that last append was the last batch
            log.debug( f'breaking loop' )
            break
        else:
            log.debug( f'increasing rows from {rows} to {rows+500}' )
            start += rows
    log.debug( f'api_data, partial, ``{pprint.pformat(api_data)[0:1000]}...``' )
    # log.debug( f'api_data, ``{pprint.pformat(api_data)}``' )
    return api_data


def merge_api_data_into_org_data( org_data: dict, api_data: list ) -> dict:
    """ Merges API data into org data.
        Called by manage_org_mods_update(). """
    for api_item in api_data:
        hh_id = api_item['mods_id_local_ssim'][0]
        if hh_id in org_data:
            org_data[ hh_id ]['pid'] = api_item['pid']
    log.debug( f'updated org_data, partial, ``{pprint.pformat(org_data)[0:1000]}...``' )
    # log.debug( f'org_data, ``{pprint.pformat(org_data)}``' )
    ## confirm all items have pid -----------------------------------
    ids_missing_pids = []
    for hh_id, item_dict in org_data.items():
        if 'pid' not in item_dict:
            ids_missing_pids.append( hh_id )
    if ids_missing_pids:
        log.warning( f'WARNING: these items are missing pids: ``{ids_missing_pids}``' )
    return org_data
    

def get_item_tracker_filepath( hh_id: str, tracker_directory_path: pathlib.Path ) -> pathlib.Path:
    """ Gets the item's tracker file path.
        Called by manage_org_mods_update(). 
    Doctest:
    >>> get_item_tracker_filepath( 'HH123456', pathlib.Path('/path/to/foo') )    
    PosixPath('/path/to/foo/HH12/3456/HH123456__item_updated.json')
    >>> get_item_tracker_filepath( 'HH123456_0001', pathlib.Path('/path/to/foo') )    
    PosixPath('/path/to/foo/HH12/3456/HH123456_0001__item_updated.json')
    """
    part_a, part_b = hh_id[:4], hh_id[4:8]
    item_tracker_filepath = tracker_directory_path / part_a / part_b / f'{hh_id}__item_updated.json'  # pathlib way of joining paths
    log.debug(f'item_tracker_filepath, ``{item_tracker_filepath}``')
    return item_tracker_filepath


def call_api( path: str, pid: str ) -> str:
    """ Calls the API.
        Called by manage_org_mods_update(). """
    log.debug( f'path, ``{path}``; pid, ``{pid}``' )
    ## call the binary ---------------------------------------------
    env_copy = os.environ.copy()
    # cmd = [ BINARY_PATH, '--check_envars', 'True']; break  # will show envars perceived by the binary
    cmd = [ BINARY_PATH, '--mods_filepath', path, '--bdr_pid', pid ]
    log.debug( f'cmd, ``{cmd}``' )
    result: subprocess.CompletedProcess = subprocess.run( cmd, env=env_copy, capture_output=True, text=True )
    log.debug( f'result, ``{result}``' )
    ## log and return errors ----------------------------------------
    return_data = ''
    if result.stderr:
        log.warning( f'WARNING, stderr returned, ``{result.stderr}``' )
        return_data = result.stderr
    log.debug( f'return_data, ``{return_data}``' )
    return return_data


def update_item_tracker( item_tracker_filepath: pathlib.Path, err: str ) -> None:
    """ Updates the item's tracker file.
        - If there's no error, the current filename will be used, eg, `HH001545_0001__item_updated.json` and will be empty.
        - If there's an error, the file-name will be renamed, eg, `HH001545_0001__problem.json` and will contain the error.
        Called by manage_org_mods_update(). """
    ## ensure parent-paths exist ------------------------------------
    item_tracker_filepath.parent.mkdir( parents=True, exist_ok=True )
    ## write to file ------------------------------------------------
    # err = 'foo-error'  # for testing
    timestamp: str = time.strftime( '%Y-%m-%d %H:%M:%S', time.localtime() )
    if not err:
        msg = json.dumps( {'timestamp': timestamp, 'message': 'all_good'}, sort_keys=True, indent=2 )
        with open( item_tracker_filepath, 'w' ) as f:
            f.write( msg )
    else:
        existing_filename = item_tracker_filepath.name
        new_filename = existing_filename.replace( '__item_updated.json', '__item_problem.json' )
        new_filepath = item_tracker_filepath.parent / new_filename
        err_msg = json.dumps( {'timestamp': timestamp, 'err': err}, sort_keys=True, indent=2 )
        with open( new_filepath, 'w' ) as f:
            f.write( err_msg )
    return


def update_org_tracker( org_tracker_filepath: pathlib.Path ) -> None:
    """ Updates the org's tracker file.
        Called by manage_org_mods_update(). 
        TODO:
        - store hh_id/pid errors here. 
        - perhaps have org-elapsed time.
        - perhaps have total-item-count and items-updated count. """
    ## ensure parent-paths exist ------------------------------------
    org_tracker_filepath.parent.mkdir( parents=True, exist_ok=True )
    ## write to file ------------------------------------------------
    timestamp: str = time.strftime( '%Y-%m-%d %H:%M:%S', time.localtime() )
    msg = json.dumps( {'timestamp': timestamp, 'message': 'org_processed'}, sort_keys=True, indent=2 )
    with open( org_tracker_filepath, 'w' ) as f:
        f.write( msg )
    return


## helpers end ------------------------------------------------------


## manager ----------------------------------------------------------
def manage_org_mods_update( orgs_list: list, 
                            mods_directory_path: pathlib.Path, 
                            tracker_directory_path: pathlib.Path ) -> None:
    """ Manager function
        Called by dundermain. """
    for org in orgs_list:
        log.info( f'\n\nprocessing org, ``{org}``' )
        org_tracker_filepath: pathlib.Path = get_org_tracker_filepath( org, tracker_directory_path )
        org_already_processed: bool = check_tracker( org_tracker_filepath )
        if org_already_processed:
            continue
        org_data: dict = get_filepath_data( org, mods_directory_path )  # value-dict contains path info at this point
        api_data: list = get_org_data_via_api( org )
        org_data: dict = merge_api_data_into_org_data( org_data, api_data )
        for i, (hh_id, item_dict) in enumerate( org_data.items() ):
            if i > 2:  # for testing, will process the org-mods and first item-mods
                break
            path: str = item_dict['path']; pid: str = item_dict['pid']
            log.info( f'\nprocessing item ``{hh_id}-{pid}``\n' )
            item_tracker_filepath: pathlib.Path = get_item_tracker_filepath( hh_id, tracker_directory_path )
            item_already_processed: bool = check_tracker( item_tracker_filepath ) 
            if item_already_processed:
                continue  
            err: str = call_api( path, pid )
            update_item_tracker( item_tracker_filepath, err )
        update_org_tracker( org_tracker_filepath )
        log.info( f'finished processing org, ``{org}``' )
    return


## dunndermain ------------------------------------------------------
if __name__ == '__main__':
    """ Receives and validates dir-path, then calls manager function. """
    assert pathlib.Path.cwd().name == 'bdr_scripts_public', f"Error: wrong directory; cd to the `bdr_sripts_public` directory and try again."
    start_time = time.monotonic()
    ## prep args ----------------------------------------------------
    parser: argparse.ArgumentParser = config_parser()
    ## grab args ----------------------------------------------------
    args: argparse.Namespace = parser.parse_args()
    orgs_list = [ ', '.join( args.org_list.split(',') ) ]
    # mods_directory_path = pathlib.Path( args.mods_dir )
    mods_directory_path = pathlib.Path( args.mods_dir ).resolve()  # if a relative-path is submitted, this will resolve it to an absolute path
    tracker_directory_path = pathlib.Path( args.tracker_dir ).resolve()
    run_envar_check: str = args.check_envars
    ## validate path-------------------------------------------------
    validate_arg_paths( mods_directory_path, tracker_directory_path )
    ## check envars -------------------------------------------------
    if run_envar_check and run_envar_check.lower() == 'true':
        display_envars()
    ## get to work --------------------------------------------------
    manage_org_mods_update( orgs_list, mods_directory_path, tracker_directory_path )
    elapsed_time = time.monotonic() - start_time
    log.info( f'total elapsed time for all orgs, ``{elapsed_time:.2f}`` seconds' )
