import src.wal as wal
import src.store as store
import time
from pathlib import Path
import re
# Check that log matches hint
def name_matches_hint(log:Path, hint:Path):
    log_parts = log.parts
    hint_parts = hint.parts
    return "h"+log_parts[-1] == hint_parts[-1]

# Determine log number.
def log_id(log:Path) -> int:
    match = re.search(r"([0-9]*)\.bin",log.parts[-1])
    log_id = '0'
    if match:
        log_id = match.group(1)
    return int(log_id)

# Determine the deleted keys(tombstones) for a given set of files
def tombstones(files:list[Path]) -> dict:
    tombstones:dict = {}
    for file in files:
        tombstones = wal.compactWal(tombstones, file, "tombstones")
    return tombstones

# Determine the key value hash for a given set of files
def merged_kv(files:list[Path]) -> dict:
    merged_kv:dict = {}

    for file in files:
        merged_kv = wal.compactWal(merged_kv, file, "value")
    return merged_kv

# Create a hint file at the hint name of loc
def create_hint_file(hints:dict[str,int], loc:Path) -> bool:
    for key, val in hints.items():
        wal.wal_append(wal.package_hint_kv(key, val), hint_name(loc))
    return True

# Create log and hint files for given dict of tombstones and key values
# (tombstones placed at beginning)
def create_log_and_hint(tombstones:dict[str,str], merged_kv:dict, loc:Path) -> bool:
    hints:dict[str,int] = {}

    for tombstone_key, tombstone_value in tombstones.items():
        store.remove(tombstone_key,loc,{})

    for key, value in merged_kv.items():
        store.put(key, value, loc, hints)

    create_hint_file(hints, loc)

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

# create a sorted list of segments (newest is first)
# a segment is a tuple[log file, hint file]
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
            if name_matches_hint(log,hint):
                res.append((log,hint))
                has_hint = True
        if not has_hint:
            res.append((log,Path("")))

    res.sort(key=lambda x: log_id(x[0]), reverse=True)
    return res

# Determine the next segment of cur
def segment_iter(directory:Path, cur:Path)-> Path:
    segments = get_segments(directory)
    if segments and cur.parts[-1] == "active.bin":
        return segments[0][0]

    for i in range(1,len(segments)):
        if log_id(cur) > log_id(segments[i][0]):
            return segments[i][0]

    return Path("")

# return Path for the hintfile of a given log
def hint_name(log:Path) -> Path:
    name = log.parts[-1]
    hint_name = "h" + name
    return log.parent / hint_name

# remove the "t" for temporary files
def remove_t(path):
    new_name = path.parts[-1][1:]
    return path.parent / new_name

# takes a list of files without hint files or "active" determines the oldest one
def tmp_name(files:list[Path]) -> Path:
    files.sort(key=lambda path: log_id(path))
    file = files[0]
    return file.parent / ("t" + file.parts[-1])

# remove the files in the processed_files list
# set the tmp file name to the new file name
def remove_old_set_new(files:list[Path], new_name:Path, tmp_name:Path) -> bool:
    remove(files)
    swap_names(tmp_name, new_name)
    swap_names(hint_name(tmp_name), hint_name(new_name))
    return True

# create new log, remove old logs
def replace(logs:list[Path]) -> bool:
    tmp_name = tmp_name(logs)
    new_name = remove_t(tmp_name)

    return (create_log_and_hint(tombstones(logs),
                                merged_kv(logs),
                                tmp_name)
            and remove_old_set_new(logs,new_name,tmp_name))


# controller to execute background merge and compact functions
# attempts on an interval decided by every_x_sec.
def compact_and_merge(every_x_sec:float, directory, threshold) -> bool:
    start_time = time.monotonic()
    counter = 0
    while True:
        replace(wal.should_merge(get_segments(directory),threshold))
        time.sleep(every_x_sec - ((time.monotonic() - start_time) % every_x_sec))

    return False
