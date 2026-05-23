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

# Add key value into a given log
def put_helper(key:str, val:str, log:Path) -> bool:
    wal.wal_append(wal.package_kv(key,val,package_type=0), log)
    return True

# Format and append key value pair to active file. Update in-memory hash
def put(key:str, val:str, directory:Path, imh:dict[str,int], c_thresh) -> bool:
    active = directory / "active.bin"
    offset = wal.offset(active)
    put_helper(key, val, active)
    myhash.update(key, offset, imh)
    if offset >= c_thresh:
        seg.new_active_file(directory)
        imh.clear()
    return True


# format and append tombstone; update in memory hash
def remove(key:str, directory:Path,imh:dict[str,int]) -> str:
    active = directory / "active.bin"
    wal.wal_append(wal.package_kv(key,"",package_type=1), active)
    myhash.delete(key, imh)
    return "DELETE succeeded"


# takes the action and splits the processing
def process(directory:Path, in_memory_hash:dict, action:str, key:str, value:str="", compaction_threshold=100) -> str:
    if action == "GET":
        res = fetch(key,directory,in_memory_hash)
        if res:
            return res
        else:
            return "GET failed"
    elif action == "PUT":
        if put(key,value,directory,in_memory_hash, compaction_threshold):
            return "PUT succeeded"
        else:
            return "PUT failed"
    elif action == "DELETE":
        return remove(key,directory,in_memory_hash)
    else:
        return "Error"

