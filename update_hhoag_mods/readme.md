## Steps

- (done) run `01_make_orgs_file.py` to produce a text file ("data_files/01_orgs.txt") of the 97 orgs to be passed to the pipeline's make_dirs.py script.

- (done) get the 97 org-MODS.

- (done) run the pipeline's `make_dirs.py` script pointing to the directory of all 97 org-MODS to produce all the org and item MODS files. Notes:
    - This needs to be run on the server where the mount to the hhoag-images exists, because the script uses the image-scan directories (given that it's purpose is to create directories for eventual full-pipeline file-processing).
    - The `make_dirs.py` outputs 13,530 files (about 60MB), so they're not stored in this repo, but at `parent_dir/all_97_orgs_mods_xml_files/`. Note that make_dirs.py outputs a structure like `orgA` dir, which contains the `orgA.mods.xml` file, and subdirs like `orgA_0001` dir, which contains the `orgA_0001.mods.xml` file.

- run the future `02_gather_mods_paths.py` to create a json file ("data_files/02_mods_paths.json") of an identifier-to-path dict
    - example: {
        'HH001545_0001': { 'path': '/path/to/HH001545_0001_mods.xml'}
        etc.
        }