from pathlib import Path
import zlib
import src.my_hash as myhash
import src.wal as wal
import src.segment_manager as seg

# check if offset is valid. -1 is invalid flag
def offset_is_valid(offset:int) -> bool:
    return offset >= 0


# Determine the value of a given key.
# Returns empty string if doesn't exist
def fetch(key:str, directory:Path, imh:dict[str,int]) -> str:
    cur = directory / "active.bin"
    while cur.is_file():
        if cur.parts[-1] == "active.bin":
            if myhash.contains(key, imh):
                offset = myhash.get_offset(key, imh)
                return wal.read(offset,cur)
        else:
            hint = wal.read_hint_file(seg.hint_name(cur))
            print(hint)
            if myhash.contains(key, hint):
                offset = myhash.get_offset(key,hint)
                return wal.read(offset, cur)
        cur = seg.segment_iter(directory, cur)
    return ""

# Format and append key value pair to active file. Update in-memory hash
def put(key:str, value:str, directory:Path, imh:dict[str,int]) -> bool:
    active_file = directory / "active.bin"
    offset = wal.offset(active_file)
    return (wal.wal_append(wal.package_kv(key,value,package_type=0), active_file)
                and myhash.update(key, offset, imh))

# format and append tombstone; update in memory hash
def remove(key:str, storage:Path,imh:dict[str,int]) -> str:
    wal.wal_append(wal.package_kv(key,"",package_type=1), storage)
    myhash.delete(key, imh)
    return "DELETE succeeded"


# takes the action and splits the processing
def process(directory:Path, in_memory_hash:dict, action:str, key:str, value:str="") -> str:

    active_file = directory / "active.bin"
    if action == "GET":
        res = fetch(key,directory,in_memory_hash)
        if res:
            return res
        else:
            return "GET failed"
    elif action == "PUT":
        if put(key,value,directory,in_memory_hash):
            return "PUT succeeded"
        else:
            return "PUT failed"
    elif action == "DELETE":
        return remove(key,active_file,in_memory_hash)
    else:
        return "Error"


# # search the inactive files for the key
# def search(key:str,directory:Path) -> tuple[Path,dict]:
#     # files = seg.get_files(directory)
#     files = wal.get_logs(directory)
#     cur_hash:dict = {}
#     for file, hint_file in files:
#         if hint_file:
#             cur_hash = wal.compactWal(cur_hash, hint_file, "value_as_int")
#         else:
#             # there is a chance to optimize here by setting compactWal to "value"
#             print(file)
#             cur_hash = wal.compactWal(cur_hash, file, "offset")
#         if key in cur_hash:
#             return (file, cur_hash)
#     # an empty hash returns offset_value of -1
#     # which trigers get failed in read()
#     return (Path(""), {})

