## Purpose to update bdr mods files with new mods files

## Steps

- note: initially i'll do this step by step; eventually it'd be good to have one script that can be passed orgs (or a path to a text-file of orgs), which would perform all the steps.

- (done) run `01_make_orgs_file.py` to produce a text file ("data_files/01_orgs.txt") of the 97 orgs to be passed to the pipeline's make_dirs.py script.

- (done) ensure the 97 org-MODS are in-place.

- (done) run the pipeline's `make_dirs.py` script pointing to the directory of all 97 org-MODS to produce all the org and item MODS files. Notes:
    - This needs to be run on the server where the mount to the hhoag-images exists, because the script uses the image-scan directories (given that it's purpose is to create directories for eventual full-pipeline file-processing).
    - The `make_dirs.py` outputs 13,530 files (about 60MB), so they're not stored in this repo, but at `parent_dir/all_97_orgs_mods_xml_files/`. Note that make_dirs.py outputs a structure like `orgA` dir, which contains the `orgA.mods.xml` file, and subdirs like `orgA_0001` dir, which contains the `orgA_0001.mods.xml` file.

- (done) run the `02_gather_mods_paths.py` to create a json file of an identifier-to-path dict
    - example: {
        'HH001545_0001': { 'path': '/path/to/HH001545_0001_mods.xml'},
        etc.
        }
    - this will be the initial version of the essential source-data to update a mods-record:
        - the filepath to the new-mods
        - the pid
    - the file will be saved to '../support_stuff/update_hhoag_orgs_support_stuff/02b_hhoag_mods_paths.json' -- so not within the repo, since it contains paths.

- run the future `03_acertain_pids.py` to create a json file ("data_files/03_mods_paths_and_pids.json").
    - example: {
        'HH001545_0001': { 'path': '/path/to/HH001545_0001_mods.xml', 'pid: 'the_pid' },
        etc.
        }

- start the `04_update_all_mods.py` script by determining what files to update by examining the "tracker".
    - create a tracker system
        - simplest: add a 'status' entry to the filepath/pid dict
            - downside, the json file should be re-written each time, meaning overhead and the inability to run the script concurrently without semaphore or mutex code
        - more code: use a tracker similar to the pipeline's tracker.

- run the code.

- future:
    - make this into a single-script, as noted in the first step-note.
    - call the actual update-mods code as a binary (test load/time/memory performance)
