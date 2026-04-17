import re
import csv
from pathlib import Path
import src.my_hash as myhash
import src.wal as wal

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

def process_put(key:str,value:str) -> bytes:
    key_bytes = key.encode("utf-8")
    value_bytes = value.encode("utf-8")

    return (len(key_bytes).to_bytes(4,"big")
            + key_bytes
            + len(value_bytes).to_bytes(4,"big")
            + value_bytes)

def offset_is_valid(offset:int) -> bool:
    return offset >= 0

def process(action:str, key:str, value:str, inMemoryHash:dict, storage:str) -> str:
    if action == "GET":
        offsetValue = myhash.get_offset(key,inMemoryHash)

        if offset_is_valid(offsetValue):
            return wal.read(offsetValue,storage)
        else:
            return "GET failed"

    elif action == "PUT":

        storageOffset = wal.offset(storage)
        wal.append(process_put(key,value), storage)

        myhash.update(key, storageOffset, inMemoryHash)
        return "PUT succeeded"
    else:
        return "Parse failed"


