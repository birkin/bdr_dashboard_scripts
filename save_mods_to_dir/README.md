# Purpose

## What this does

Takes a list of pids, and an output-directory, and 
- Saves the MODS to the directory
- Maybe? Saves a json mapping-file to the same directory, where each element of the mapper contains:
    - the saved MODS filepath
    - the BDR pid

## Reason for existence

We need to update some hall-hoag org-MODS files. An initial BDR-API query will get us the org-items and pids. Then the pids will be passed to this script, to gather the MODS files. This concept of gathering MODS-files will likely be useful in the future.

---