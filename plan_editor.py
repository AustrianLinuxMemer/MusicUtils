#!/usr/bin/python3
import sqlite3
import sys
import os
import re
import shlex
import datetime
import typing


class PlanEntry:
    def __init__(self, id: int, old_name: str, new_name: str, is_file: bool):
        self.id = id
        self.old_name = old_name
        self.new_name = new_name
        self.is_file = is_file
    def new_name_message(self): return f"(ID {self.id}) {self.old_name} needs an conformant name"
    def __str__(self): return f"{self.id}|{self.old_name}|{self.new_name}|{self.is_file}"


class Statistics:
    def __init__(self, total_files, completed_files, total_directories, completed_directories):
        self.total_files = total_files
        self.completed_files = completed_files
        self.total_directories = total_directories
        self.completed_directories = completed_directories

    def __str__(self):
        return f"files: {self.completed_files}/{self.total_files} ({round(self.completed_files / self.total_files * 100, 2)}% completed) directories: {self.completed_directories}/{self.total_directories} ({round(self.completed_directories / self.total_directories * 100, 2)}% completed)"

class ProgramController:
    def __init__(self, db_str: str):
        self.db_str = db_str
        self.statistics = None
        self.valid_filename = re.compile("[a-zA-Z0-9\\-]+")
    @staticmethod
    def update_name(connection: sqlite3.Connection, new_name: str, id: int) -> None:
        cursor = connection.cursor()
        cursor.execute("UPDATE Plan SET new_name = ? WHERE id = ?", (new_name, id))

    def input_new_name(self, entry: PlanEntry):
        name, ext = os.path.splitext(entry.old_name)
        obj_kind = "file" if entry.is_file else "directory"
        print(f"(#{entry.id} [{obj_kind}]): {entry.old_name} needs an new name")
        while True:
            user_input = input("> ")
            if self.valid_filename.fullmatch(user_input):
                if entry.is_file:
                    return f"{user_input}{ext}"
                else:
                    return user_input
            else:
                print("Please enter a valid filename [0-9a-zA-Z and '-']")

    @staticmethod
    def input_yes_no(default: bool=False) -> bool:
        prompt = "[Y/n] > " if default else "[y/N] > "
        default_letter = "y" if default else "n"
        result = default
        while True:
            try:
                user_input = input(prompt)
                if user_input.lower().startswith("y"):
                    result = True
                    break
                elif user_input.lower().startswith("n"):
                    result = False
                    break
                elif not user_input:
                    break
                else:
                    print(f"Please enter a valid option [y/n] or press Enter to accept {default_letter}")
            except KeyboardInterrupt:
                continue
            except EOFError:
                continue
        return result

    def batch_update_names(self):
        with sqlite3.connect(self.db_str) as conn:
            cursor = conn.cursor()
            cursor.execute("BEGIN TRANSACTION")
            cursor.execute("SELECT id, old_name, new_name, file FROM Plan WHERE new_name IS NULL")
            rows = [PlanEntry(*row) for row in cursor.fetchall()]
            for entry in rows:
                try:
                    new_name = self.input_new_name(entry)
                    self.update_name(conn, new_name, entry.id)
                except KeyboardInterrupt:
                    print()
                    break
                except EOFError:
                    print()
                    break
            else:
                print("End of plan entries reached")
            print("Do you want to save? [y/n]")
            save = self.input_yes_no()
            if save:
                cursor.execute("COMMIT")
            else:
                cursor.execute("ROLLBACK")

    @staticmethod
    def get_regex_lambda(pattern: str, helper: typing.Callable[[PlanEntry], str], full_match=False) -> typing.Callable[[PlanEntry], bool] | None:
        try:
            regex = re.compile(pattern)
            if full_match:
                return lambda entry: bool(regex.fullmatch(helper(entry)))
            else:
                return lambda entry: bool(regex.match(helper(entry)))
        except re.error:
            return None
    def get_list_filters(self, field: str, filter_type: str, arg1: str, arg2: str):
        with sqlite3.connect(self.db_str) as conn:
            query = lambda cur: cur.execute("SELECT * FROM Plan")
            queries = {
                "eq": (lambda cur: cur.execute("SELECT * FROM Plan WHERE ? = ?", (field, arg1))),
                "!eq": (lambda cur: cur.execute("SELECT * FROM Plan WHERE NOT ? = ?", (field, arg1))),
                "none": (lambda cur: cur.execute("SELECT * FROM Plan WHERE ? is NULL", (field,))),
                "!none": (lambda cur: cur.execute("SELECT * FROM Plan WHERE NOT ? is NULL", (field,))),
                "range": (lambda cur: cur.execute("SELECT * FROM Plan WHERE ? >= ? AND ? <= ?"), (field, arg1, field, arg2)),
                "!range": (lambda cur: cur.execute("SELECT * FROM Plan WHERE NOT (? >= ? AND ? <= ?)"), (field, arg1, field, arg2)),
            }

            allowed_fields = {
                "id": lambda entry: str(entry.id),
                "old_name": lambda entry: entry.old_name,
                "new_name": lambda entry: entry.new_name,
                "file": lambda entry: str(entry.file)
            }

            if field not in allowed_fields:
                print(f"Field {field} is not allowed")
                return

            if filter_type in queries:
                query = queries[filter_type]

            def parse_bool(arg: str) -> bool:
                if arg.lower() == "true":
                    return True
                else:
                    return False

            filters = {
                "regex": self.get_regex_lambda(arg1, allowed_fields[field], parse_bool(arg2)) if filter_type == "regex" else None,
                "substr": lambda entry: arg1 in allowed_fields[field](entry) if filter_type == "substr" else None,
            }

            cursor = conn.cursor()
            query(cursor)
            for row in cursor.fetchall():
                entry = PlanEntry(*row)
                if filter_type not in filters:
                    print(entry)
                elif filters[filter_type](entry):
                    print(entry)



    def list_entries(self, field: str, filter_type: str, arg1: str, arg2: str):




    def begin(self):


if not sys.argv[1]:
    sys.exit("Specify a Changeplan database")


pc = ProgramController(sys.argv[1])
pc.begin()