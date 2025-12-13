import sys
import json
import os
def ask_user(old, is_file=False):
    ext = None
    if is_file:
        old, ext = os.path.splitext(old)

    def valid_name(name):
        if ext:
            return name and name.isascii() and not "." in name
        else:
            return name and name.isascii()

    def format_name(name):
        if ext:
            return f"{name}{ext}"
        else:
            return name
    obj_kind = "file" if is_file else "directory"
    while True:
        print(f"{obj_kind} {old} needs an ASCII name")
        user_input = input(f"Enter new name for this {obj_kind}: ")
        if valid_name(user_input):
            return format_name(user_input)
        else:
            print(f"{user_input} is not valid")

def save_file(new_path, old_changeplan, new_file_dict, new_dir_dict):
    with open(new_path, "w", encoding="utf-8") as fd:
        fd.seek(0)
        fd.truncate()
        if not old_changeplan:
            old_changeplan = {}
        if not old_changeplan["files"]:
            old_changeplan["files"] = {}
        if not old_changeplan["directories"]:
            old_changeplan["directories"] = {}
        for old_entry, new_entry in new_file_dict.items():
            old_changeplan["files"][old_entry] = new_entry
        for old_entry, new_entry in new_dir_dict.items():
            old_changeplan["directories"][old_entry] = new_entry
        json.dump(old_changeplan, fd, ensure_ascii=False, indent=4)

if not sys.argv[1]:
    sys.exit("Specify a Changeplan input file")

if not sys.argv[2]:
    sys.exit("Specify a Changeplan output file")

with open(sys.argv[1], "r", encoding="utf-8") as changeplan_file:
    json_plan = json.load(changeplan_file)
    print("Press CTRL+C to exit discarding changes, Press CTRL+D to exit with saving")
    new_files = {}
    new_directories = {}
    try:
        if "files" in json_plan:
            for old_file_name, new_file_name in json_plan["files"].items():
                if not new_file_name:
                    new_name = ask_user(old_file_name, is_file=True)
                    new_files[old_file_name] = new_name
        if "directories" in json_plan:
            for old_dir_name, new_dir_name in json_plan["directories"].items():
                if not new_dir_name:
                    new_name = ask_user(old_dir_name)
                    new_directories[old_dir_name] = new_name
        input("Press Enter to confirm all, press CTRL+C to discard")
        save_file(sys.argv[2], json_plan, new_files, new_directories)
    except EOFError:
        print("Saving File")
        save_file(sys.argv[2], json_plan, new_files, new_directories)
    except KeyboardInterrupt:
        exit(0)