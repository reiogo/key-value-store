from pathlib import Path
import os
import src.wal as wal
import csv

def recreate_hash(storageLocation:str) -> dict:
    p = Path(storageLocation)
    myhash = {}
    offset = 0
    try:
        while offset != os.path.getsize(p.resolve()):
            key,next_offset = wal.iter_wal(offset,storageLocation)
            myhash[key] = offset
            offset = next_offset

    except Exception as e:
        print(f"Error: {e}")

    return myhash

def get_offset(key:str, h:dict) -> int:
    return h.get(key, -1)

def update(key:str, offset:int, h:dict) -> bool:
    h[key] = offset
    return h[key] == offset
