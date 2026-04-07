import re
import csv
from pathlib import Path
import my_hash as myhash

def parser(raw_data:str) -> tuple[str, str, str]:
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

def process_put(key:str,value:str,storage:str) ->bool:
    p = Path(storage)
    try:
        if key:
            with p.open("a") as f:
                offset = f.tell()
                f.write(f'{key},{value}\n')
                #return offset
                print(offset)
                return offset
    except Error as e:
        print(f"Error: {e}")


def process_get(key:str, storage:str, offset:int) -> str:
    p = Path(storage)
    res = ""
    if not key:
        return ""
    if p.exists():
        with p.open("r") as file:
            file.seek(offset, 0)
            reader = csv.reader(file)
            reader = reader.__next__()
            if len(reader) > 1 and reader[0] == key:
                res = reader[1]
    return res

def process(action:str, key:str, value:str, storage:str = '/usr/key-value/storage/tmp.txt') -> str:
    inMemoryHash = myhash.create()

    if action == "GET":
        offset = myhash.get_offset(key,inMemoryHash)
        if offset:
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


