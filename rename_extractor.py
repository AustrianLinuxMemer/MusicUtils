import sqlite3
import sys
import json


with sqlite3.connect(sys.argv[1]) as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT id, old_name FROM Plan WHERE new_name IS NULL")
    rows = cursor.fetchall()
    rows = sorted(rows, key=lambda row: len(row[1] or ""), reverse=True)
    cursor.execute("SELECT MAX(id) FROM Plan WHERE new_name IS NULL")
    max_id = cursor.fetchone()[0]
    if max_id is None:
        print("No new names needed")
        exit(0)
    max_len = len(str(abs(int(max_id))))
    def number(x: int) -> str:
        return f"{x:0{max_len}d}"
    with open(sys.argv[2], "w", encoding="utf-8") as f:
        f.write("{\n")
        for i, row in enumerate(rows):
            comma = "," if i < len(rows) - 1 else ""
            json_safe_old_name = json.dumps(row[1], ensure_ascii=False)
            json_safe_id = json.dumps(number(row[0]), ensure_ascii=False)
            f.write(f'{json_safe_id}: [{json_safe_old_name},\t""]{comma}\n')
        f.write("}")