# Remove photo duplicates based on their similarity score and on their size.

Works on Unix and macOS

## How to use
Make sure `main.py`is executable:
```
cd .../path/to/this/project/...
chmod +x main.py
```

Move all the photos you want to check for duplicated in a single folder.
## WARNING: Make sure to back up all your photos, I will not be responsible for any data loss caused by this script.
Launch `main.py`:
```
./main.py -p /path/to/the/target/folder -m 1.10 -s 0.90
```
With:
-m specifying the maximum size ratio between two photos to be checked for equality. A higher ratio means more time to complete the execution.
-s The minimum similarity score between two photos to be considered the same.
-p The path to the folder containing the images.

