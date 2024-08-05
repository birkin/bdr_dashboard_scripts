# Purpose

## What this does

Takes a list of Hall-Hoag org-codes, or a file of org-codes, and...
- Saves the org-only MODS files to a specified directory.
- Saves a json mapping file to the same directory, where each element of the mapper contains:
    - the org-code
    - the saved MODS filepath
    - the BDR pid for the org-item

## Reason for existence

We need to update some org-MODS. This script will gather the MODS that will be updated.

---