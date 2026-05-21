import src.wal as wal
import src.store as store
import time
from pathlib import Path
import re

def tombstones(files:list[Path]) -> dict:
    tombstones:dict = {}
    for file in files:
        tombstones = wal.compactWal(tombstones, file, "tombstones")
    return tombstones

# Goes through files and creates a
# hash of the keys and values
def merged_kv(files:list[Path]) -> dict:
    merged_kv:dict = {}

    for file in files:
        merged_kv = wal.compactWal(merged_kv, file, "value")
    return merged_kv

# use tombstones and merged_kv to create a new log 
# (the tombstones are placed at the beginning because they are only the unaffected tombstones)
def create_log_and_hint(tombstones:dict[str,str], merged_kv:dict, new_log_loc:Path) -> bool:
    hints:dict[str,int] = {}

    for tombstone_key, tombstone_value in tombstones.items():
        store.process_delete(tombstone_key,new_log_loc,{})

    for key, value in merged_kv.items():
        store.process_put(key, value, new_log_loc, hints)

    for hint_key, hint_value in hints.items():
        store.process_put(hint_key, str(hint_value), hint_name(new_log_loc), {})

    return True

# swap Path names
def swap_names(new:Path,old:Path) -> bool:
    p = Path(new)
    p.rename(Path(old))
    return True

# removes segments and their hint files from the directory
def remove(segments:list[Path]) -> bool:
    for file in segments:
        file.unlink(missing_ok=True)
        hint_name(file).unlink(missing_ok=True)
    return True

# create a sorted list of segments
# a segment is a tuple[segment file, hint file]
def get_segments(directory:Path)->list[tuple[Path,Path]]:
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
            if wal.name_matches_hint(log,hint):
                res.append((log,hint))
                has_hint = True
        if not has_hint:
            res.append((log,Path("")))

    res.sort(key=lambda x: x[0])
    return res

# gets the files from the storage directory
def get_files(directory:Path)->list[Path]:
    res:list[Path] = []
    for child in directory.iterdir():
        res.append(child)
    return res

# return Path for the hintfile of a given log
def hint_name(log:Path) -> Path:
    name = log.parts[-1]
    hint_name = "h" + name
    return log.parent / hint_name

# remove the "t" for temporary files
def remove_t(path):
    new_name = path.parts[-1][1:]
    return path.parent / new_name

# remove the files in the processed_files list
# set the tmp file name to the new file name
def remove_old_set_new(files:list[Path], new_name:Path, tmp_name:Path) -> bool:
    remove(files)
    swap_names(tmp_name, new_name)
    swap_names(hint_name(tmp_name), hint_name(new_name))
    return True

# takes a list of files without hint files or "active" determines the oldest one
def tmp_name(files:list[Path]) -> Path:
    files.sort(key=lambda x: x[0])
    return file[0]

def replace(target_segments:list[Path]) -> bool:
    tmp_name = tmp_name(target_segments)
    new_name = remove_t(tmp_name)

    return (create_log_and_hint(tombstones(target_segments),
                                merged_kv(target_segments),
                                tmp_name)
            and remove_old_set_new(target_segments,new_name,tmp_name))


# controller to execute background merge and compact functions
def compact_and_merge(every_x_sec:float, directory, threshold) -> bool:
    start_time = time.monotonic()
    counter = 0
    while True: #don't run all of the time, because that's unnecessary overhead
        segments = get_segments(directory)
        replace(wal.should_compact(segments))
        if counter > 10:
            replace(wal.should_merge(segments, threshold))
            counter = 0
        time.sleep(every_x_sec - ((time.monotonic() - start_time) % every_x_sec))

    return False

# determine the name
# def tmp_name(not_this:list[Path]=[]) -> Path:
#     files = get_files(directory)
#     i = len(files) - 1
#     top = files[i][0]
#     while i > -1 and top in not_this:
#         i -= 1
#         top = files[i][0]

#     top_log_parts = top.parts
#     name = top_log_parts[-1]
#     match = re.search(r"([0-9]*)\.bin",name)
#     log_id = '0'
#     if match:
#         log_id = match.group(1)
#     new_id = str(int(log_id) + 1)
#     new_name = new_id + ".bin"
#     return top.parent / new_name
