from pathlib import Path
import os
import src.wal as wal
import csv

def recreate_hash(storageLocation:str) -> dict:
    p = Path(storageLocation)
    myhash = {}
    check_passed = True
    offset = 0
    try:
        while offset != os.path.getsize(p.resolve()) and check_passed:
            check_passed,package_type,key,next_offset = wal.iter_wal(offset,storageLocation)
            if package_type == 0:
                myhash[key] = offset
            elif package_type == 1:
                delete(key, myhash)
            offset = next_offset

    except Exception as e:
        print(f"Error: {e}")

    return myhash

def get_offset(key:str, h:dict) -> int:
    return h.get(key, -1)

def update(key:str, offset:int, h:dict) -> bool:
    h[key] = offset
    return h[key] == offset

def delete(key:str, h:dict) -> bool:
    value = h.pop(key, False)
    return value != False
