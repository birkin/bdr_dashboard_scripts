"""
Script takes a list of BDR-PIDs and downloads the MODS files to the specified directory.
Typical usage:
$ python save_mods.py --output_dir_path "/path/to/output_dir" --pids_list_path "/path/to/bdr_pids.txt"
"""

import argparse, logging, os, pathlib, pprint, sys
from dotenv import load_dotenv, find_dotenv


## load envars ------------------------------------------------------
""" dotenv only used for optional log-level envar """
dotenv_abs_path = pathlib.Path(__file__).resolve().parent.parent.parent / '.env'
assert dotenv_abs_path.exists(), f'file does not exist, ``{dotenv_abs_path}``'
load_dotenv( 
    find_dotenv( str(dotenv_abs_path), raise_error_if_not_found=True ), 
    override=True 
    )
LOGLEVEL: str = os.environ.get( 'SM__LOGLEVEL', 'DEBUG' )  # 'DEBUG' or 'INFO'


## setup console logging --------------------------------------------
lglvldct = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO }
logging.basicConfig(
    level=lglvldct[LOGLEVEL],  # assigns the level-object to the level-key loaded from the envar
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger( __name__ )


## helpers start (manager function is after helpers) ----------------


def config_parser() -> argparse.ArgumentParser:
    """ Configures the argument parser.
        Called by parse_args(). """
    desc = """Downloads MODS files to the specified directory, for given PIDS. 
- Takes an output-directory filepath and a list of BDR-PIDS (or a file of BDR-PIDS) as arguments. 
- More info: <https://github.com/Brown-University-Library/bdr_scripts_public/blob/main/save_mods/readme.md>.
"""
    parser = argparse.ArgumentParser( description=desc, formatter_class=argparse.RawTextHelpFormatter )
    parser.add_argument( '--output_dir_path', required=True, help='required; full-path to the output_directory' )
    parser.add_argument( '--pids_list_path', required=False, help='required if no `pids_list` flag; filepath to a file of BDR-PIDs, one PID per line' )
    # parser.add_argument( '--pids_list', required=False, help='required if no `--pids_list_path` flag; comma-separated string of BDR-PIDs' )
    parser.add_argument( '--check_envars', required=False, action='store_true', help='optional; displays envars, and exits' )
    # parser.add_argument( '--version', action='store_true', help='optional; shows git commit hash, and exits' )
    return parser


def display_envars() -> None:
    """ Displays envars.
        Called by parse_args(). """
    print( f'''

Envars:
          
For this `save_mods.py` script...
- LOGLEVEL, ``{LOGLEVEL}``

(end)
''')
    sys.exit( 0 )
    return


## mamager functions ------------------------------------------------

def parse_args():
    """ Configures arg-parser and calls manager function.
        Called by dundermain. """
    ## config parser ------------------------------------------------
    parser: argparse.ArgumentParser = config_parser()
    ## grab args ----------------------------------------------------
    args = parser.parse_args()
    ## version check ------------------------------------------------
    # if args.version:
    #     print( f'version-{COMMIT_HASH}' ); return
    ## check envars -------------------------------------------------
    if args.check_envars :
        display_envars(); return
    ## get to work  -------------------------------------------------
    output_dir_path = args.output_dir_path
    pids_list_path = args.pids_list_path
    log.debug( f'output_filepath: {output_dir_path}' )
    log.debug( f'pids_list_path: {pids_list_path}' )
    if not output_dir_path or not pids_list_path:
        print( 'Both --output_dir_path and --pids_list_path are required.' )
        sys.exit( 1 )
    ## call manager -------------------------------------------------
    download_mods( output_dir_path, pids_list_path )
    return

## dundermain  ------------------------------------------------------
if __name__ == '__main__':
    parse_args()
