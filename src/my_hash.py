from pathlib import Path
import src.wal as wal

def recreate_hash(storage:Path) -> dict:
    return wal.compactWal({}, storage / "active.bin", "offset")

def get_offset(key:str, h:dict[str,int]) -> int:
    return h.get(key, -1)

def get_value(key:str, h:dict[str,str]) -> str:
    return h.get(key, "")

def update(key:str, offset:int, h:dict[str,int]) -> bool:
    h[key] = offset
    return h[key] == offset

def delete(key:str, h:dict) -> bool:
    value = h.pop(key, False)
    return value != False

def contains(key, h:dict) -> bool:
    return key in h
