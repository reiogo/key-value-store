from pathlib import Path
import csv

def recreate_hash(storageLocation:str) -> dict:
    p = Path(storageLocation)
    myhash = {}
    offset = 0
    try:
        with p.open("r") as file:
            while True:
                offset = file.tell()
                line = file.readline()
                if not line:
                    break
                key = line.split(",")[0]
                myhash[key] = offset

    except Exception as e:
        print(f"Error: {e}")

    return myhash

def get_offset(key:str, h:dict) -> int:
    return h.get(key, -1)

def update(key:str, offset:int, h:dict) -> bool:
    h[key] = offset
    return h[key] == offset
