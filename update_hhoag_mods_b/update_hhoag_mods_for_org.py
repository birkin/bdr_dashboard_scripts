"""
Example usage:
    $ python ./update_hhoag_mods.py --org_list "fooA,fooB" --mods_dir "bar" --tracker_dir "baz" 
"""

import argparse, json, logging, os, pathlib, sys, time


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


## helpers ----------------------------------------------------------


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


## manager ----------------------------------------------------------
def manage_org_mods_update( orgs_list: list, mods_directory_path: pathlib.Path, tracker_directory_path: pathlib.Path ) -> None:
    """ Manager function
        Called by dundermain. """
    for org in orgs_list:
        org_already_processed: bool = check_org_in_tracker( org, tracker_directory_path )
    return


def check_org_in_tracker( org: str, tracker_directory_path: pathlib.Path ) -> bool:
    """ Checks if org is already in tracker file.
        Called by manage_org_mods_update(). """
    tracker_file_path = tracker_directory_path.joinpath( f'{org}_tracker.json' )
    if tracker_file_path.exists():
        log.debug( f'org `{org}` already in tracker' )
        return True
    else:
        log.debug( f'org `{org}` not in tracker' )
        return False


## dunndermain ------------------------------------------------------
if __name__ == '__main__':
    """ Receives and validates dir-path, then calls manager function. """
    assert pathlib.Path.cwd().name == 'bdr_scripts_public', f"Error: wrong directory; cd to the `bdr_sripts_public` directory and try again."
    start_time = time.monotonic()
    ## prep args ----------------------------------------------------
    parser = argparse.ArgumentParser(description='Recursively finds JSON files in specified directory.')
    parser.add_argument( '--org_list', required=True, help='orgs to process; example "HH123456" or "HH123456,HH654321"' )
    parser.add_argument( '--mods_dir', required=True, help='path to directory containing pre-made org-mods and item-mods files' )
    parser.add_argument( '--tracker_dir', required=True, help='path to directory containing the tracker files' )
    args = parser.parse_args()
    ## grab args ----------------------------------------------------
    orgs_list = [ ', '.join( args.org_list.split(',') ) ]
    mods_directory_path = pathlib.Path(args.mods_dir)
    tracker_directory_path = pathlib.Path(args.tracker_dir)
    ## validate path-------------------------------------------------
    validate_arg_paths( mods_directory_path, tracker_directory_path )
    ## get to work --------------------------------------------------
    manage_org_mods_update( orgs_list, mods_directory_path, tracker_directory_path )
    elapsed_time = time.monotonic() - start_time
    log.info( f'elapsed time, ``{elapsed_time:.2f}`` seconds' )
