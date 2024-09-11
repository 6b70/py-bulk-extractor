# py-bulk-extractor

Quick and dirty Python wrapper around 7z for bulk extraction of archives. Automates extracting a directory of encrypted archives with password list.
Password list is passed in as a text file list of lines.

- Supports extraction of various archive formats supported by 7z.
- Kind of fast password checking with a user-provided list for encrypted archives.

This script is for when you are too lazy to manually match known passwords to a bunch of archives. 

A lot of bulk extraction libs/apps either fail to fully extract all archive types, lack support for certain formats, or don't always handle password-protected archives well (RAR5 💀). This just invokes 7z for everything 

### Requirements:
- Python 3.x
- 7z (must be installed and in your system's PATH)

TODO:
I am going to add recursive extraction support at some point.