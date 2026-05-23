from pathlib import Path
import os
import zlib
import src.my_hash as myhash
import re
import src.segment_manager as seg

# Compute hash from a given log file
# package_type ={ 0 is append, 1 is delete}
# val_type is "offsets" or "values"
def create_hash(hsh:dict, log:Path, val_type) -> dict:
    check_passed = True
    offset = 0
    try:
        while offset != log.stat().st_size and check_passed:
            check_passed,package_type,key,value,next_offset = read_wal(offset,log)
            if package_type == 0:
                if val_type == "offsets":
                    hsh[key] = offset
                elif val_type == "values":
                    hsh[key] = value
            elif package_type == 1:
                myhash.delete(key, hsh)
            offset = next_offset

    except Exception as e:
        print(f"Error: {e}")
    return hsh

# Compute dictionary of tombstoned values for a given log
def create_tombstones(hsh:dict, log:Path) -> dict:
    check_passed = True
    offset = 0
    try:
        while offset != log.stat().st_size and check_passed:
            check_passed,package_type,key,value,next_offset = read_wal(offset,log)
            if package_type == 0 and key in hsh:
                myhash.delete(key,hsh)
            if package_type == 1:
                hsh[key] = ""
            offset = next_offset

    except Exception as e:
        print(f"Error: {e}")
    return hsh

# Compute size of file, which is the offset
def offset(storage:Path) -> int:
    try:
        with storage.open("ab") as file:
            return file.tell()
    except OSError as e:
        raise RuntimeError(f"Getting offset failed. Path: {storage}") from e

# Compute the byte string for a given key/value pair
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

# Compute byte representation of a hint key/value pair
def package_hint_kv(key:str, val:int) -> bytes:
    s_val = str(val)
    key_bytes = key.encode("utf-8")
    value_bytes = s_val.encode("utf-8")

    return (len(key_bytes).to_bytes(4,"big")
            + key_bytes
            + len(value_bytes).to_bytes(4,"big")
            + value_bytes)

# Read given hint file
# Close file when val is an empty string.
def read_hint_file(hint:Path) -> dict[str,int]:
    try:
        hashmap = {}
        with hint.open("rb") as file:
            while True:
                klen_raw = file.read(4)
                klen = int.from_bytes(klen_raw, byteorder="big")
                k_raw = file.read(klen)
                key = k_raw.decode("utf-8")

                vlen_raw = file.read(4)
                vlen = int.from_bytes(vlen_raw, byteorder="big")
                v_raw = file.read(vlen)
                value = v_raw.decode("utf-8")
                if value == "":
                    break
                hashmap[key] = int(value)
        return hashmap
    except OSError as e:
        raise RuntimeError(f"Function: read_hint_file failed. Path: {hint}") from e



# Add bytes to a given file
# Return offset
def wal_append(word:bytes, storage:Path) -> int:
    storage.touch(exist_ok=True)
    try:
        with storage.open("ab") as f:
            f.write(word)
            return f.tell()
    except OSError as e:
        raise RuntimeError(f"Wal append failed. Path: {storage}") from e

# I could pass the checksum results into here, but it should because iter_wal is building the hash. Though, I'm not sure that logic is always correct.
def read(offset:int, storage:Path) -> str:
    check_passed,package_type,key,value,offset = read_wal(offset, storage)
    return value

# Read all information about the key/value data from a given offset
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

