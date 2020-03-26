# Release Notes

## Version 0.1.10 (hotfix)
  * Included requests library in requirements.txt

## Version 0.1.9
  * Added "global" verbose option.  
  * Updated in-package schema and unit tests for VERIS version 1.3.4  
  * Better URL handling, better type checking  
  
## Version 0.1.8
  * Cleaned up a problem in `_enums_from_schema` where the default parameters were mutable
  objects and the list could potentially grow and grow and grow...
  * Cleaned up the documentation and type checking in `_enums_from_schema`  

## Version 0.1.7
  * Fixed problem with verbose=False not silencing all outputs in the `VERIS` class (`/veris/veris.py`).
  * Cleaned up leading space after semicolons in `/veris/veris.py`.

## Version 0.1.6  
  * Changes the name of this file from `NEWS.md` to `Release_Notes.md`  
  * Fixes problem with `__version__` declaration in `__init.md__` file.  

## Version 0.1.5
  * Now the full industry name is created along with the short name.  

## Version 0.1.4  
  * Fixed Industry typo: Accomodation -> Accommodation  
  * Prints a warning if no json files found in specified directory. Previous behavior simply returned an empty Data Frame, which caused some users confusion.  
  * Adds a tqdm status bar to the long-running parts of `json_to_df`.  

## Version 0.1.3
  * Updated requirements.txt file to be >= rather than ==

## Version 0.1.2
  * First stable release.