import re
import csv
from pathlib import Path
def parser(raw_data) -> tuple[str, str, str]:
    data = raw_data.decode("utf-8")

    pat = re.compile(r"(GET|PUT)\s?([^ ]*)?\s?([^ ]*)?")
    m = pat.search(data)

    if m:
        action = m.group(1)
        key = m.group(2)
        value = m.group(3)
        return (action, key, value)
    else:
        return ("NULL", "", "")

def put_process(key,value) ->bool:
    p = Path('/usr/key-value/storage/tmp.txt')
    if p.exists():
        with p.open("a") as f:
            f.write(f'{key},{value}\n')
        return True
    else:
        return False


def get_process(key) -> str:
    p = Path('/usr/key-value/storage/tmp.txt')
    if p.exists():
        with p.open() as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == key:
                    return row[1]
    return ""

def process(action, key, value) -> str:
    if action == "GET":
        return get_process(key)
    elif action == "PUT":
        put_process(key, value)
        return ""

    else:
        return ""


