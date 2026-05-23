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

# Determine the deleted keys(tombstones) for a given set of sorted files
# files should be in oldest to most recent order
def tombstones(files:list[Path]) -> dict:
    tombstones:dict = {}
    for file in files:
        tombstones = wal.create_tombstones(tombstones, file)
    return tombstones

# Determine the key value hash for a given set of files
# files should be in oldest to most recent order
def merged_kv(files:list[Path]) -> dict:
    merged_kv:dict = {}

    for file in files:
        merged_kv = wal.create_hash(merged_kv, file, "values")
    return merged_kv

# Create a hint file at the hint name of loc
def create_hint_file(hints:dict[str,int], loc:Path) -> bool:
    hint = hint_name(loc)
    hint.touch(exist_ok=True)
    for key, val in hints.items():
        wal.wal_append(wal.package_hint_kv(key, val), hint)
    return True


# Create log and hint files for given dict of tombstones and key values
# (tombstones placed at beginning)
def create_log_and_hint(tombstones:dict[str,str], merged_kv:dict, loc:Path) -> bool:
    hints:dict[str,int] = {}
    loc.touch(exist_ok=True)
    for t_key, t_val in tombstones.items():
        wal.wal_append(
            wal.package_kv(t_key,"",package_type=1),
            loc)

    offset = 0
    for key, val in merged_kv.items():
        hints[key] = offset
        offset = wal.wal_append(
            wal.package_kv(key,val,package_type=0),
            loc)

    create_hint_file(hints, loc)

    return True

# swap Path names
def swap_names(old:Path,new:Path) -> bool:
    old.rename(new)
    return True

# removes segments and their hint files from the directory
def remove_seg_and_hint(segments:list[Path]) -> bool:
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

# takes a list of files without hint files or "active" determines the oldest one
def active_file_tmp_name(directory:Path) -> Path:
    segments = get_segments(directory)
    if not segments:
        return directory / "1.bin"
    else:
        file = segments[0][0]
        return file.parent / (str(log_id(file)+1) +".bin")

# remove the files in the processed_files list
# set the tmp file name to the new file name
def remove_old_set_new(files:list[Path], new:Path, tmp:Path) -> bool:
    remove_seg_and_hint(files)
    swap_names(tmp, new)
    swap_names(hint_name(tmp), hint_name(new))
    return True

# create new log, remove sorted list of logs 
# input: files in oldest to newest
def replace(to_replace:list[Path]) -> bool:
    tmp = tmp_name(to_replace)
    new = remove_t(tmp)

    return (create_log_and_hint(tombstones(to_replace),
                                merged_kv(to_replace),
                                tmp)
            and remove_old_set_new(to_replace, new, tmp))

# Compact the active file, and reset it
def new_active_file(directory:Path) -> bool:
    new = active_file_tmp_name(directory)
    active = directory / "active.bin"
    to_replace = [active]

    create_log_and_hint(tombstones(to_replace),
                                merged_kv(to_replace),
                                new)
    active.unlink()
    active.touch()
    return True


# determines which files should be merged
# returns a list of files without the hint files
# input is sorted from newest to oldest
# output is sorted from oldest to newest
def should_merge(files:list[tuple[Path,Path]], threshold) -> list[Path]:
    files.reverse()
    res = []
    total_size = 0
    for file, hint_file in files:
        total_size += file.stat().st_size
        if total_size > threshold:
            break
        res.append(file)
    return res


# controller to execute background merge and compact functions
# attempts on an interval decided by every_x_sec.
def compact_and_merge(every_x_sec:float, directory, threshold) -> bool:
    start_time = time.monotonic()
    counter = 0
    while True:
        replace(should_merge(get_segments(directory),threshold))

        # calculate how often to merge
        time.sleep(every_x_sec - ((time.monotonic() - start_time) % every_x_sec))

    return False
