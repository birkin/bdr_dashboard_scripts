"""
- Creates json file of all mods-filepaths, with the key being the hall-hoag-id 
    (eg `HH123456` for orgs, or `HH123456_0001` for items). 
Purpose: this json file will be enhanced with bdr-pids in a later step.
Usage: python ./update_hhoag_mods/02_gather_mods_paths.py
Output: ./update_hhoag_mods/data_files/02b_hhoag_mods_paths.json

Note that one of the functions has a doctest. All doctests can be run with the following command:
`python -m doctest ./update_hhoag_mods/02_gather_mods_paths.py -v`
"""

import argparse, logging, os, pathlib, pprint, sys, time


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


def start_id_dict( directory_path: pathlib.Path ) -> dict:
    """ Manager function
        - gets paths
        - makes dict
        - saves to json
        Called by dundermain. """
    mods_files: list = make_mods_paths_list( directory_path)
    id_dict: dict = make_id_dict( mods_files )


def make_id_dict( mods_files: list ) -> dict:
    """ Returns dict with hall-hoag-ids as keys and mods-filepaths as values.
        Called by start_id_dict() """
    id_dict = {}
    for mods_file in mods_files:
        mods_file_str = str( mods_file )
        hh_id = mods_file_str.split('/')[-1].split('_')[0]
        id_dict[ hh_id ] = mods_file_str
    log.debug( f'id_dict[0:3], ``{pprint.pformat(id_dict[0:3])}``' )
    return id_dict

def parse_id( mods_file: pathlib.Path ) -> str:
    """ Returns hall-hoag-id from mods-filepath.
        Called by make_id_dict() 
    >>> mods_file = pathlib.Path( '/path/to/HH123456_0001_mods.xml' )
    >>> parse_id( mods_file )
    'HH123456'
    """
    mods_file_str = str( mods_file )
    hh_id = mods_file_str.split('/')[-1].split('_')[0]
    log.debug( f'path, ``{mods_file_str}``; hh_id, ``{hh_id}``' )
    return hh_id


def make_mods_paths_list( directory_path: pathlib.Path ) -> list:
    """ Returns non-sorted list of pathlib-paths of mods-files.
        Called by start_id_dict() """
    mods_paths_list = list( directory_path.rglob('*mods.xml') )
    log.debug( f'len(mods_paths_list), ``{len(mods_paths_list)}``' )
    log.debug( f'mods_paths_list[0:3], ``{pprint.pformat(mods_paths_list[0:3])}``' )
    return mods_paths_list


if __name__ == '__main__':
    """ Receives and validates dir-path, then calls manager function. """
    start_time = time.monotonic()
    ## handle args --------------------------------------------------
    parser = argparse.ArgumentParser(description='Recursively finds JSON files in specified directory.')
    parser.add_argument('--dirpath', required=True, help='Path to the directory to search')
    args = parser.parse_args()
    directory_path = pathlib.Path(args.dirpath)
    ## validate path-------------------------------------------------
    if not directory_path.exists():
        print( f'Error: The path {directory_path} does not exist.', file=sys.stderr )
        sys.exit(1)
    if not directory_path.is_dir():
        print( f'Error: The path {directory_path} is not a directory.', file=sys.stderr )
        sys.exit(1)
    ## get to work --------------------------------------------------
    start_id_dict( directory_path )
    elapsed_time = time.monotonic() - start_time
    log.info( f'elapsed time, ``{elapsed_time:.2f}`` seconds' )
