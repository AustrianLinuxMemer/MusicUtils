import os
import sqlite3
import sys

def write_select_results_as_tsv(file: str, tuples: list):
    max_digits = len(str(max(i for i, *_ in tuples)))
    def lpad(i: int):
        i_digits = len(str(i))
        return "0"*(max_digits-i_digits)+str(i)

    with open(file, 'w', encoding="utf-8") as f:
        for id, *rest in tuples:
            rest_str = "\t".join(str(r) for r in rest)
            f.write(f"{lpad(id)}\t{rest_str}\n")

def get_flac_files(cursor: sqlite3.Cursor, file: str):
    cursor.execute('SELECT id, title, tracknumber, extension FROM flacfiles WHERE new_name IS NULL')
    flac_list = sorted(cursor.fetchall(), key=lambda x: len(x[1]), reverse=True)
    write_select_results_as_tsv(file, flac_list)

def get_other_files(cursor: sqlite3.Cursor, file: str):
    cursor.execute('SELECT id, old_name, extension FROM otherfiles WHERE new_name IS NULL')
    other_list = sorted(cursor.fetchall(), key=lambda x: len(x[1]), reverse=True)
    write_select_results_as_tsv(file, other_list)

def get_directories(cursor: sqlite3.Cursor, file: str):
    cursor.execute('SELECT id, old_name FROM directories WHERE new_name IS NULL')
    directory_list = sorted(cursor.fetchall(), key=lambda x: len(x[1]), reverse=True)
    write_select_results_as_tsv(file, directory_list)

with sqlite3.connect(sys.argv[1]) as conn:
    cursor = conn.cursor()
    get_flac_files(cursor, sys.argv[2])
    get_other_files(cursor, sys.argv[3])
    get_directories(cursor, sys.argv[4])
