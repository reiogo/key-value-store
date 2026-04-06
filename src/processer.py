import re
import csv
from pathlib import Path
def parser(raw_data) -> tuple[str, str, str]:
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

def put_process(key,value,storage) ->bool:
    p = Path(storage)
    if p.exists() and key:
        with p.open("a") as f:
            f.write(f'{key},{value}\n')
        return True
    else:
        return False


def get_process(key, storage) -> str:
    p = Path(storage)
    res = ""
    if p.exists():
        with p.open() as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) > 1 and row[0] == key:
                    res = row[1]
    return res

def process(action, key, value, storage = '/usr/key-value/storage/tmp.txt') -> str:
    if action == "GET":
        return get_process(key,storage)
    elif action == "PUT":
        put_process(key, value,storage)
        return ""
    else:
        return ""


