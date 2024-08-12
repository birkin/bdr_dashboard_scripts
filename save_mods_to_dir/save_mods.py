"""
Script takes a list of BDR-PIDs and downloads the MODS files, concurrently, to the specified directory.
Typical usage:
$ cd /path/to/bdr_scripts_public/save_mods_to_dir/
$ source ../../env/bin/activate
$ python ./save_mods.py --output_dir_path "/path/to/output_dir" --pids_list_path "/path/to/bdr_pids.txt"
"""

import argparse, logging, os, pathlib, pprint, sys, time
import urllib.request
import xml.etree.ElementTree as ET
from multiprocessing import Pool

from dotenv import load_dotenv, find_dotenv


## load envars & constants ------------------------------------------
# dotenv_abs_path = pathlib.Path(__file__).resolve().parent.parent.parent / '.env'
dotenv_abs_path = pathlib.Path(__file__).resolve().parent.parent.parent / '.env_save_mods_to_dir'
assert dotenv_abs_path.exists(), f'file does not exist, ``{dotenv_abs_path}``'
load_dotenv( 
    find_dotenv( str(dotenv_abs_path), raise_error_if_not_found=True ), 
    override=True 
    )
LOGLEVEL: str = os.environ.get( 'SM__LOGLEVEL', 'INFO' )  # 'DEBUG' or 'INFO'
MODS_URL_PATTERN = os.environ[ 'SM__MODS_URL_PATTERN' ]
PROCESSES = os.environ.get( 'SM__PROCESSES', 2 )  # number of processes to run in parallel


## setup console logging --------------------------------------------
lglvldct = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO }
logging.basicConfig(
    level=lglvldct[LOGLEVEL],  # assigns the level-object to the level-key loaded from the envar
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger( __name__ )


## helpers start (manager functions are after helpers) --------------


def config_parser() -> argparse.ArgumentParser:
    """ Configures the argument parser.
        Called by parse_args(). """
    desc = """Downloads MODS files, concurrently, to the specified directory, for given PIDS. 
- Takes an output-directory filepath, and a filepath to a list of BDR-PIDS, as arguments.
- More info: <https://github.com/Brown-University-Library/bdr_scripts_public/blob/main/save_mods_to_dir/README.md>.
"""
    parser = argparse.ArgumentParser( description=desc, formatter_class=argparse.RawTextHelpFormatter )
    parser.add_argument( '--check_envars', required=False, action='store_true', help='optional; displays envars, and exits' )
    parser.add_argument( '--output_dir_path', required=False, help='required; full-path to the output_directory' )
    parser.add_argument( '--pids_list_path', required=False, help='required if no `pids_list` flag; filepath to a file of BDR-PIDs, one PID per line' )
    # parser.add_argument( '--pids_list', required=False, help='required if no `--pids_list_path` flag; comma-separated string of BDR-PIDs' )
    # parser.add_argument( '--version', action='store_true', help='optional; shows git commit hash, and exits' )
    return parser


def display_envars() -> None:
    """ Displays envars.
        Called by parse_args(). """
    print( f'''
Envars:
          
For this `save_mods.py` script...
- LOGLEVEL, ``{LOGLEVEL}``
- MODS_URL_PATTERN, ``{MODS_URL_PATTERN}``
- PROCESSES, ``{PROCESSES}``

(end)
''')
    sys.exit( 0 )
    return


def validate_path( arg_path: str ) -> pathlib.Path:
    """ Validates path.
        Called by parse_args(). """
    pth = pathlib.Path( arg_path ).resolve()  # resolve() returns a full-path
    if not pth.exists():
        raise Exception( f'path, ``{arg_path}`` does not exist``' )
    return pth
    

def make_output_filepath( output_dir_path: pathlib.Path, pid: str ) -> pathlib.Path:
    """ Creates the output filepath.
        Called by download_mods(). """
    pid_stem = ''
    if ':' in pid:
        pid_stem = pid.replace(':', '_')
    else:
        pid_stem = pid
    pid_filename = f'{pid_stem}__MODS.xml'
    output_filepath = pathlib.Path( f'{output_dir_path}/{pid_filename}' ).resolve()
    log.debug( f'output_filepath, ``{output_filepath}``' )
    return output_filepath


def grab_and_save_mods( url: str, output_filepath: pathlib.Path, pid: str ):
    """ Grabs and saves the MODS file.
        Called by download_mods(). """
    log.debug( f'url, ``{url}``' )
    log.debug( f'about to call urlopen() for pid, ``{pid}``' )
    try:
        with urllib.request.urlopen( url ) as response:
            if response.status == 200:
                log.debug( f'got a 200 response for pid, ``{pid}``' )
                with open( output_filepath, 'wb' ) as mods_output_file:
                    mods_output_file.write( response.read() )
            else:
                log.warning( f'failed to retrieve the file for pid, ``{pid}``. HTTP status code: {response.status}' )
    except Exception as e:
        log.warning( f'error, ``{e}``' )
    return


def check_well_formed_xml( output_filepath: pathlib.Path, pid: str ):
    """ Checks if the file is well-formed XML. """
    try:
        ET.parse( output_filepath)
        validity = True
    except ET.ParseError:
        validity = False
        log.warning( f'MODS for pid, ``{pid}`` is not valid xml' )
    log.debug( f'validity, ``{validity}``' )
    return


## mamager functions ------------------------------------------------


# def download_mods( pid: str, output_dir_path: pathlib.Path ) -> None:
def download_mods( pid: str, output_dir_path: pathlib.Path, index: int ) -> None:
    """ Manager function.
        Downloads MODS files to the specified directory, for given PIDS.
        Called by parse_args(). """
    log.debug( f'processing pid, ``{pid}``' )
    url = MODS_URL_PATTERN.format( PID_VAR=pid )
    log.debug( f'url, ``{url}``' )
    output_filepath: pathlib.Path = make_output_filepath( output_dir_path, pid )
    grab_and_save_mods( url, output_filepath, pid )
    check_well_formed_xml( output_filepath, pid )
    ## show progress ------------------------------------------------
    if (index + 1) % 10 == 0:
        log.info(f'Processed {index + 1} items.')
    return


def run_multiprocessing( output_dir_path: pathlib.Path, pids_list_path: pathlib.Path ) -> None:
    """ Manager function.
        Runs the download_mods function in parallel processes.
        Called by parse_args(). 
        Note: if I were just passing a pid to download_mods, I could use `pool.map( pids )`,
            but `pool.starmap()` allows for additional arguments. """
    with open( pids_list_path, 'r' ) as pids_file:
        pids: list = pids_file.read().splitlines()
        log.info( f'pids to process, ``{pprint.pformat(pids)}``' )
    with Pool( processes=PROCESSES ) as pool:
        # args = [ (pid, output_dir_path) for pid in pids ]
        args = [ (pid, output_dir_path, index) for index, pid in enumerate(pids) ]
        pool.starmap( download_mods, args )        
    return


def parse_args():
    """ Configures arg-parser and calls manager function.
        Called by dundermain. """
    ## config parser ------------------------------------------------
    parser: argparse.ArgumentParser = config_parser()
    ## grab args ----------------------------------------------------
    args = parser.parse_args()
    ## check envars -------------------------------------------------
    if args.check_envars :
        display_envars(); return
    ## check required args ------------------------------------------
    if not args.output_dir_path or not args.pids_list_path:
        print( 'Both --output_dir_path and --pids_list_path are required.' )
        sys.exit( 1 )
    ## validate paths -----------------------------------------------
    output_dir_path: pathlib.Path = validate_path( args.output_dir_path )
    pids_list_path: pathlib.Path = validate_path( args.pids_list_path )
    ## call manager function just above -----------------------------
    # download_mods( output_dir_path, pids_list_path )
    run_multiprocessing( output_dir_path, pids_list_path )
    return


## dundermain  ------------------------------------------------------
if __name__ == '__main__':
    start_time = time.monotonic()
    parse_args()
    elapsed_time = time.monotonic() - start_time
    log.info( f'total elapsed time, ``{elapsed_time:.2f}`` seconds' )
