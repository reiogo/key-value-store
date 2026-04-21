from pathlib import Path
import zlib
import src.my_hash as myhash
import src.wal as wal

# check if offset is valid. -1 is invalid flag
def offset_is_valid(offset:int) -> bool:
    return offset >= 0

# search the inactive files for the key
def search(key:str,directory:Path) -> tuple[Path,dict]:
    files = wal.get_logs(directory)
    cur_hash:dict = {}
    for file, hint_file in files:
        if hint_file:
            cur_hash = wal.compactWal(cur_hash, hint_file, "value_as_int")
        else:
            # there is a chance to optimize here by setting compactWal to "value"
            print(file)
            cur_hash = wal.compactWal(cur_hash, file, "offset")
        if key in cur_hash:
            return (file, cur_hash)
    # an empty hash returns offset_value of -1
    # which trigers get failed in process_get()
    return (Path(""), {})

# get key from active file. If not there then check older files
def process_get(key:str, directory:Path, storage:Path,imh:dict[str,int]) -> str:
    offset_value = myhash.get_offset(key,imh)
    if offset_is_valid(offset_value):
        if myhash.contains(key, imh):
            return wal.read(offset_value,storage)
        else:
            old_log, hints = search(key,directory)
            return process_get(key, directory, old_log, hints)
    else:
        return "GET failed"

# format and append key value pair; update in memory hash
def process_put(key:str,value:str,storage:Path,imh:dict[str,int]) -> bool:
        storage_offset = wal.offset(storage)
        return (wal.wal_append(wal.package_kv(key,value,package_type=0), storage)
                and myhash.update(key, storage_offset, imh))

# format and append tombstone; update in memory hash
def process_delete(key:str, storage:Path,imh:dict[str,int]) -> str:
    wal.wal_append(wal.package_kv(key,"",package_type=1), storage)
    myhash.delete(key, imh)
    return "DELETE succeeded"


# takes the action and splits the processing
def process(directory:Path, in_memory_hash:dict, action:str, key:str, value:str="") -> str:

    active_file = directory / "active.bin"
    if action == "GET":
        return process_get(key,directory,active_file,in_memory_hash)
    elif action == "PUT":
        if process_put(key,value,active_file,in_memory_hash):
            return "PUT succeeded"
        else:
            return "PUT failed"
    elif action == "DELETE":
        return process_delete(key,active_file,in_memory_hash)
    else:
        return "Error"


