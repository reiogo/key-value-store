from pathlib import Path
import os
import zlib
import src.my_hash as myhash
import re
def name_matches_hint(log:Path, hint:Path):
    log_parts = log.parts
    hint_parts = hint.parts
    return "h"+log_parts[-1] == hint_parts[-1]

def next_name(all_logs:list[tuple[Path,Path]],not_this:list[Path]=[]) -> Path:
    i = len(all_logs) - 1
    top = all_logs[i][0]
    while i > -1 and top in not_this:
        i -= 1
        top = all_logs[i][0]

    top_log_parts = top.parts
    name = top_log_parts[-1]
    match = re.search(r"([0-9]*)\.bin",name)
    log_id = '0'
    if match:
        log_id = match.group(1)
    new_id = str(int(log_id) + 1)
    new_name = new_id + ".bin"
    return top.parent / new_name

def new_hint_name(log:Path) -> Path:
    log_parts = log.parts
    name = log_parts[-1]
    hint_name = "h" + name
    return log.parent / hint_name


def remove_from_wal(logs_to_remove:list[Path], all_logs:list[tuple[Path,Path]]) -> list[tuple[Path,Path]]:
    updated_logs = []
    for file, hint in all_logs:
        if file not in logs_to_remove:
            updated_logs.append((file,hint))
        else:
            file.unlink()
            if hint in logs_to_remove:
                hint.unlink()
    return updated_logs

def should_compact(files:list[tuple[Path,Path]]) -> list[Path]:
    res = []
    for file, hint_file in files:
        if hint_file == Path(""):
            res.append(file)
    return res

def should_merge(files:list[tuple[Path,Path]], threshold) -> list[Path]:
    res = []
    total_size = 0
    for file, hint_file in files:
        total_size += file.stat().st_size
        if total_size > threshold:
            break
        res.append(file)
    return res

def get_logs(directory:Path)->list[tuple[Path,Path]]:
    res:list[tuple[Path,Path]] = []
    logs = []
    hints = []
    for child in directory.iterdir():
        name = child.parts[-1]
        if name == "active.bin":
            continue
        if name[0] == 'h':
            hints.append(child)
        else:
            logs.append(child)

    for log in logs:
        has_hint = False
        for hint in hints:
            if name_matches_hint(log,hint):
                res.append((log,hint))
                has_hint = True
        if not has_hint:
            res.append((log,Path("")))

    res.sort()
    return res

def compactWal(given_hash:dict, storage:Path, value_flag) -> dict:
    check_passed = True
    offset = 0
    try:
        while offset != storage.stat().st_size and check_passed:
            check_passed,package_type,key,value,next_offset = read_wal(offset,storage)
            if package_type == 0 and value_flag != "tombstones":
                if value_flag == "offset":
                    given_hash[key] = offset
                elif value_flag == "value":
                    given_hash[key] = value
                elif value_flag == "value_as_int":
                    given_hash[key] = int(value)
            elif package_type == 1:
                myhash.delete(key, given_hash)
                if value_flag == "tombstones":
                    given_hash[key] = ""
            offset = next_offset

    except Exception as e:
        print(f"Error: {e}")
    return given_hash

def offset(storage:Path) -> int:
    try:
        with storage.open("ab") as file:
            return file.tell()
    except OSError as e:
        raise RuntimeError(f"Getting offset failed. Path: {storage}") from e

def package_kv(key:str,value:str="",package_type:int=0) -> bytes:
    package_type_byte = package_type.to_bytes(1,"big")

    key_bytes = key.encode("utf-8")
    value_bytes = value.encode("utf-8")

    package = (package_type_byte
            + len(key_bytes).to_bytes(4,"big")
            + key_bytes
            + len(value_bytes).to_bytes(4,"big")
            + value_bytes)

    checksum = zlib.crc32(package).to_bytes(4,"big")

    return package + checksum

def wal_append(word:bytes, storage:Path) -> bool:
    try:
        with storage.open("ab") as f:
            f.write(word)
            return True
    except OSError as e:
        raise RuntimeError(f"Wal append failed. Path: {storage}") from e

# I could pass the checksum results into here, but it should because iter_wal is building the hash. Though, I'm not sure that logic is always correct.
def read(offset:int, storage:Path) -> str:
    check_passed,package_type,key,value,offset = read_wal(offset, storage)
    return value

def read_wal(offset:int, storage:Path) -> tuple[bool,int,str,str,int]:
    try:
        with storage.open("rb") as file:
            file.seek(offset, 0)

            package_type_raw = file.read(1)
            package_type = int.from_bytes(package_type_raw, byteorder="big")

            key_len_raw = file.read(4)
            key_len = int.from_bytes(key_len_raw, byteorder="big")

            key_raw = file.read(key_len)
            key = key_raw.decode("utf-8")

            value_len_raw = file.read(4)
            value_len = int.from_bytes(value_len_raw,byteorder="big")

            value_raw = file.read(value_len)
            value = value_raw.decode("utf-8")

            checksum_original = int.from_bytes(file.read(4), byteorder="big")

            checksum_current = zlib.crc32(package_type_raw
                                  + key_len_raw
                                  + key_raw
                                  + value_len_raw
                                  + value_raw)
            check_passed = checksum_original == checksum_current
        return (check_passed,
                package_type,
                key,
                value,
                (offset + 13 + key_len + value_len))
    except OSError as e:
        raise RuntimeError(f"Function: read_wal failed. Path: {storage}") from e

