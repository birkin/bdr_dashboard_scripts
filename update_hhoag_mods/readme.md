## Steps

- (done) run `01_make_orgs_file.py` to produce a text file ("data_files/01_orgs.txt") of the 97 orgs to be passed to the pipeline's make_dirs.py script.

- (done) get the 97 org-MODS.

- run the pipeline's `make_dirs.py` script pointing to the directory of all 97 org-MODS to produce all the org and item MODS files.

- run the future `02_gather_item_mods_paths.py` to create a json file ("data_files/02_mods_paths.json") of an identifier-to-path dict
    - example: {
        'HH001545_0001': { 'path': '/path/to/HH001545_0001_mods.xml'}
        etc.
        }