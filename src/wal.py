from pathlib import Path
def offset(storage:str) -> int:
    p = Path(storage)
    offset = 0
    try:
        with p.open("ab") as f:
            offset = f.tell()
    except Exception as e:
        print(f"Error: {e}")

    return offset

def append(word:bytes, storage:str) -> bool:
    p = Path(storage)
    try:
        with p.open("ab") as f:
            f.write(word)
            return True
    except Exception as e:
        print(f"Error: {e}")

    return False

def read(offset:int, storage:str) -> str:
    key,value,offset = read_wal(offset, storage)
    return value

def iter_wal(offset:int, storage:str) -> tuple[str,int]:
    key,value,offset = read_wal(offset, storage)
    return (key,offset)

def read_wal(offset:int, storage:str) -> tuple[str,str,int]:
    p = Path(storage)
    try:
        with p.open("rb") as file:
            file.seek(offset, 0)

            key_len = int.from_bytes(file.read(4), byteorder="big")
            key_bytes = file.read(key_len)
            key = key_bytes.decode("utf-8")

            value_len = int.from_bytes(file.read(4),byteorder="big")
            value_bytes = file.read(value_len)
            value = value_bytes.decode("utf-8")

            return (key, value, (offset + 8 + key_len + value_len))
    except Exception as e:
        print(f"Error: {e}")
    return ("","",0)

