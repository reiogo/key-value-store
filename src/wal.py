from pathlib import Path
import zlib
def offset(storage:str) -> int:
    p = Path(storage)
    offset = 0
    try:
        with p.open("ab") as f:
            offset = f.tell()
    except Exception as e:
        print(f"Error: {e}")

    return offset

def package_kv(key:str,value:str="",tombstone:bool=False) -> bytes:
    package_type_byte = (0).to_bytes(1,"big")
    if tombstone:
        package_type_byte = (1).to_bytes(1,"big")

    key_bytes = key.encode("utf-8")
    value_bytes = value.encode("utf-8")

    package = (package_type_byte
            + len(key_bytes).to_bytes(4,"big")
            + key_bytes
            + len(value_bytes).to_bytes(4,"big")
            + value_bytes)

    checksum = zlib.crc32(package).to_bytes(4,"big")

    return package + checksum

def append(word:bytes, storage:str) -> bool:
    p = Path(storage)
    try:
        with p.open("ab") as f:
            f.write(word)
            return True
    except Exception as e:
        print(f"Error: {e}")

    return False

# I could pass the checksum results into here, but it should because iter_wal is building the hash. Though, I'm not sure that logic is always correct.
def read(offset:int, storage:str) -> str:
    check_passed,package_type,key,value,offset = read_wal(offset, storage)
    return value

def iter_wal(offset:int, storage:str) -> tuple[bool,int,str,int]:
    check_passed,package_type,key,value,offset = read_wal(offset, storage)
    return (check_passed,package_type,key,offset)

def read_wal(offset:int, storage:str) -> tuple[bool,int,str,str,int]:
    p = Path(storage)
    try:
        with p.open("rb") as file:
            file.seek(offset, 0)

            package_type_raw = file.read(1)
            package_type = int.from_bytes(package_type_raw, byteorder="big")

            key_len_raw = file.read(4)
            key_len = int.from_bytes(key_len_raw, byteorder="big")
            # print(key_len_raw, key_len)

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
                    (offset + 8 + key_len + value_len))
    except Exception as e:
        print(f"Error: {e}")
    return (False, 0,"","",0)

