import re
import csv
from pathlib import Path
import src.my_hash as myhash

def parser(raw_data:bytes) -> tuple[str, str, str]:
    data = raw_data.decode("utf-8")

    pat = re.compile(r"(GET|PUT)\s*([^\s]*)?\s*([^\s]*)?")
    m = pat.search(data)

    if m:
        action = m.group(1)
        key = m.group(2)
        value = m.group(3)
        return (action, key, value)
    else:
        return ("NULL", "", "")

def process_put(key:str,value:str,storage:str) ->int:
    p = Path(storage)
    try:
        if key:
            with p.open("a") as f:
                offset = f.tell()
                f.write(f'{key},{value}\n')
                #return offset
                return offset
    except Exception as e:
        print(f"Error: {e}")

    return 0


def process_get(key:str, storage:str, offset:int) -> str:
    p = Path(storage)
    res = ""
    if not key:
        return ""
    if p.exists():
        with p.open("r") as file:
            file.seek(offset, 0)
            reader = csv.reader(file)
            row = reader.__next__()
            if len(row) > 1 and row[0] == key:
                res = row[1]
    return res

def process(action:str, key:str, value:str, inMemoryHash:dict, storage:str) -> str:
    if action == "GET":
        offset = myhash.get_offset(key,inMemoryHash)
        if offset > -1:
            return process_get(key,storage, offset)
        else:
            return ""
    elif action == "PUT":
        offset = process_put(key, value, storage)
        if offset:
            myhash.update(key, offset, inMemoryHash)
        return ""
    else:
        return ""


