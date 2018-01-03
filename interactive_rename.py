#   Copyright 2018 Lawrence Kesteloot
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import glob
import sys
import sha
import stat
import os

# Using a hash is much slower and doesn't handle duplicate files well. Leaving this here
# because we may want to later add a way to detect duplicate files.
USE_HASH = False

# Take a filename and escape spaces. Doesn't handle all shell special characters (quotes, etc.).
def shell_friendly(filename):
    return filename.replace(" ", "\\ ")

# Return a unique identifier for this file, as a constant-width string.
def get_file_identifier(pathname):
    if USE_HASH:
        contents = open(pathname).read()
        identifier = sha.sha(contents).hexdigest()
    else:
        # Use inode number.
        s = os.stat(pathname)
        identifier = "%-15d" % s[stat.ST_INO]

    return identifier

# Generate the data file.
def generate_file():
    for filename in glob.glob("*"):
        print get_file_identifier(filename) + " " + filename

# Read the data file and rename the files.
def rename_files(data_file):
    # Read data file.
    id_to_new_filename = {}
    for line in open(data_file):
        line = line.strip()

        # Break at the first space.
        space = line.find(" ")
        if space == -1:
            sys.stderr.write("WARNING: This line has no filename: " + line)
        else:
            file_id = line[:space]
            filename = line[space + 1:].strip()
            id_to_new_filename[file_id] = filename

    # Read file identifiers from disk.
    id_to_old_filename = {}
    for filename in glob.glob("*"):
        id_to_old_filename[get_file_identifier(filename).strip()] = filename

    # Generate the script.
    for file_id, old_filename in id_to_old_filename.items():
        new_filename = id_to_new_filename.get(file_id)
        if not new_filename:
            sys.stderr.write("Identifier " + file_id + " not found in data file: " + old_filename + "\n")
        else:
            del id_to_new_filename[file_id]
            if new_filename != old_filename:
                print "mv " + shell_friendly(old_filename) + " " + shell_friendly(new_filename)

    # See if any lines in the file were unused.
    for file_id, new_filename in id_to_new_filename.items():
        sys.stderr.write("Filename not used in data file: " + new_filename + "\n")

def main():
    if len(sys.argv) == 1:
        generate_file()
    elif len(sys.argv) == 2:
        rename_files(sys.argv[1])
    else:
        sys.stderr.write("usage: RENAME.py [filename]\n")

if __name__ == "__main__":
    main()

