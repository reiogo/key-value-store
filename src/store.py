from pathlib import Path
import zlib
import src.my_hash as myhash
import src.wal as wal

def offset_is_valid(offset:int) -> bool:
    return offset >= 0

def process(storage:str, inMemoryHash:dict, action:str, key:str, value:str="") -> str:
    if action == "GET":
        offsetValue = myhash.get_offset(key,inMemoryHash)

        if offset_is_valid(offsetValue):
            return wal.read(offsetValue,storage)
        else:
            return "GET failed"

    elif action == "PUT":

        storageOffset = wal.offset(storage)
        wal.append(wal.package_kv(key,value), storage)

        myhash.update(key, storageOffset, inMemoryHash)
        return "PUT succeeded"
    elif action == "DELETE":
        wal.append(wal.package_kv(key,value,tombstone=True), storage)
        myhash.delete(key, inMemoryHash)
        return "DELETE succeeded"
    else:
        return "Parse failed"


