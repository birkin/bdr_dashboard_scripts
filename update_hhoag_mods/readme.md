## Purpose
- to update a hall-hoag organization's bdr mods files with new mods files.

## Usage

- call the script with:
    - a list of orgs ('orgA,orgB') or a filepath to a list of orgs
    - the directory-path that contains the pre-produced mods-files in some sub-directories
	- the directory-path to the tracker-files

- example usage:
    ```
    $ python ./update_hhoag_mods.py --org_list "fooA,fooB" --mods_dir "bar" --tracker_dir "baz" 
    ```

## Flow

- check the tracker to see if the whole-org has already been processed. Assuming not...
- make an org-data-dict, where each key is the hhoag-id, and the value is {'path': 'the_path'}
- make recursive bdr-public-api queries on the org to get the necessary doc-data for the org.
- parse out the hhoag-id and the pid from the api-query-docs and update the org-data-dict, where each entry is like: 
    ```
    {
        'HH123456: {'path': 'the_path', 'pid': 'the_pid'},
        'HH123456_0001': {'path': 'the_path', 'pid': 'the_pid'},
        etc...  
    } 
    ```

- for each entry in the org-data-dict, 
	- check the tracker to see if the entry has already been processed.
	- call the update-single-mods script (which takes a path and a pid) 
	- write tracker file named 'HH123456__mods_updated.json' or 'HH123456_0001__mods_updated.json'
		- make contents be {datetime: x, time-taken: x}
- after the last entry-mods has been updated, write tracker file named 'HH123456__whole_org_updated.json'
	- make contents be {datetime: x, time-taken: x}

---
