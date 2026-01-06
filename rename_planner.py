import os.path
import mutagen.flac
import sys
import sqlite3
import re

if len(sys.argv) == 2 and sys.argv[1] == "--pass":
    exit(0)

if len(sys.argv) < 2:
    sys.exit("Please provide arguments")

symbol_table = {
    "!": "em",
    "#": "pound",
    "$": "dollar",
    "%": "percent",
    "&": "and",
    "*": "star",
    "+": "plus",
    ",": "comma",
    ".": "dot",
    "<": "lt",
    "=": "equals",
    ">": "gt",
    "?": "qm",
    "@": "at",
    "^": "caret",
    "|": "pipe",
    "~": "tilde"
}


alphanumerical_regex = re.compile("[a-zA-Z0-9]")

def get_replacement(symbol):
    return symbol_table.get(symbol, "")

def transform(string):
    symbols = list(string)
    blocks = []
    current_block = []
    for symbol in symbols:
        if alphanumerical_regex.fullmatch(symbol):
            current_block.append(symbol)
        else:
            if current_block:
                blocks.append("".join(current_block))
                current_block = []
            replacement = get_replacement(symbol)
            if replacement:
                blocks.append(replacement)
    if current_block:
        blocks.append("".join(current_block))
    return "-".join(blocks).lower()

class RenameRow:
    def __init__(self, new_name: str|None, ai_suggestion: str|None=None, tracknumber: int|None=None, file_ext: str|None=None):
        self.new_name = new_name
        self.ai_suggestion = ai_suggestion
        self.tracknumber = tracknumber
        self.extension = file_ext
    def as_tuple(self):
        return self.new_name, self.ai_suggestion, self.tracknumber, self.extension

rename_plan = {
    "directories": {},
    "flacs": {},
    "others": {}
}
if not sys.argv[1]:
    sys.exit("Please provide a directory")

total_dirs = 0
total_files = 0

for root, dirs, files in os.walk(sys.argv[1], topdown=True):
    total_dirs += len(dirs)
    total_files += len(files)

processed_dirs = 0
processed_files = 0
for root, dirs, files in os.walk(sys.argv[1], topdown=False):
    for dir_name in dirs:
        processed_dirs += 1
        print(f"({processed_dirs}/{total_dirs}) Including {dir_name}")
        if dir_name.isascii():
            rename_plan["directories"][dir_name] = transform(dir_name)
        else:
            rename_plan["directories"][dir_name] = None

    for file_name in files:
        processed_files += 1
        print(f"({processed_files}/{total_files}) Including {file_name}")
        basename, ext = os.path.splitext(file_name)
        if ext == ".flac":
            flacfile = mutagen.flac.FLAC(os.path.join(root, file_name))
            title = " ".join(flacfile.tags.get("TITLE", ["No", "Title"]))
            track_number = flacfile.tags.get("TRACKNUMBER", ["00"])[0]
            if title.isascii():
                new_title = transform(title)
                rename_plan["flacs"][file_name] = (title, track_number, ext, f"{new_title}{ext}")
            else:
                rename_plan["flacs"][file_name] = (title, track_number, ext, None)
        else:
            if basename.isascii():
                new_basename = transform(basename)
                rename_plan["others"][file_name] = (ext, f"{new_basename}{ext}")
            else:
                rename_plan["others"][file_name] = (ext, None)

with sqlite3.connect(sys.argv[2]) as conn:
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS Plan")
    cursor.execute("DROP TABLE IF EXISTS FlacFiles")
    cursor.execute("DROP TABLE IF EXISTS OtherFiles")
    cursor.execute("DROP TABLE IF EXISTS Directories")
    cursor.execute("CREATE TABLE FlacFiles (id INTEGER PRIMARY KEY AUTOINCREMENT, old_name TEXT, title TEXT, tracknumber INTEGER, extension TEXT, new_name TEXT)")
    cursor.execute("CREATE TABLE OtherFiles (id INTEGER PRIMARY KEY AUTOINCREMENT, old_name TEXT, extension TEXT, new_name TEXT)")
    cursor.execute("CREATE TABLE Directories (id INTEGER PRIMARY KEY AUTOINCREMENT, old_name TEXT, new_name TEXT)")

    for old_name, new_name in rename_plan["directories"].items():
        cursor.execute("INSERT INTO Directories (old_name, new_name) VALUES (?, ?)", (old_name, new_name))

    for old_name, tupl in rename_plan["flacs"].items():
        cursor.execute("INSERT INTO FlacFiles (old_name, title, tracknumber, extension, new_name) VALUES (?, ?, ?, ?, ?)", (old_name, *tupl))

    for old_name, tupl in rename_plan["others"].items():
        cursor.execute("INSERT INTO OtherFiles (old_name, extension, new_name) VALUES (?, ?, ?)", (old_name, *tupl))