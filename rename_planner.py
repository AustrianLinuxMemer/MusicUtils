import os.path
import mutagen.flac
import sys
import sqlite3
import re

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



rename_plan = {
    "directories": {},
    "files": {}
}
if not sys.argv[1]:
    sys.exit("Please provide a directory")

for root, dirs, files in os.walk(sys.argv[1], topdown=False):
    for dir_name in dirs:
        print(f"Including {dir_name}")
        if dir_name.isascii():
            rename_plan["directories"][dir_name] = transform(dir_name)
        else:
            rename_plan["directories"][dir_name] = None
    for file_name in files:
        print(f"Including {file_name}")
        basename, ext = os.path.splitext(file_name)
        if ext == ".flac":
            flacfile = mutagen.flac.FLAC(os.path.join(root, file_name))
            title = " ".join(flacfile.tags.get("TITLE", ["No", "Title"]))
            track_number = flacfile.tags.get("TRACKNUMBER", ["00"])[0]
            if title.isascii():
                new_title = transform(title)
                rename_plan["files"][file_name] = f"{track_number}-{new_title}{ext}"
            else:
                rename_plan["files"][file_name] = None
        else:
            if basename.isascii():
                new_basename = transform(basename)
                rename_plan["files"][file_name] = f"{new_basename}{ext}"
            else:
                rename_plan["files"][file_name] = None

with sqlite3.connect("plans/change_plan.sqlite") as conn:
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS Plan")
    cursor.execute("CREATE TABLE Plan (id INTEGER PRIMARY KEY AUTOINCREMENT, file INTEGER, old_name TEXT, new_name TEXT)")
    for key, value in rename_plan["files"].items():
        cursor.execute("INSERT INTO Plan(file, old_name, new_name) VALUES (?, ?, ?) ", (1, key, value))
    for key, value in rename_plan["directories"].items():
        cursor.execute("INSERT INTO Plan(file, old_name, new_name) VALUES (?, ?, ?) ", (0, key, value))