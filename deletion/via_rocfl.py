import logging

## 3rd party
from dotenv import load_dotenv, find_dotenv

## load envars
load_dotenv( find_dotenv(raise_error_if_not_found=True) )
STORAGE_ROOT_PATH = os.environ['DEL__STORAGE_ROOT_PATH']


def delete_item( pid ):
    print( f"Deleting {item_id}" )
## cd to repo root


