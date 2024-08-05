## load envars ------------------------------------------------------
dotenv_path = pathlib.Path(__file__).resolve().parent.parent.parent / '.env'
assert dotenv_path.exists(), f'file does not exist, ``{dotenv_path}``'
# print( f'dotenv_path, ``{dotenv_path}``' )
load_dotenv( 
    find_dotenv( str(dotenv_path), raise_error_if_not_found=True ), 
    override=True 
    )
# envars = dict(os.environ)
# print( f'envars after dotenv load, ``{pprint.pformat(dict(envars))}``' )