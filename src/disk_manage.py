import src.wal as wal
import src.store as store
import time
from pathlib import Path

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
# at new_log_loc and new hint at new_hint_loc
# (the tombstones are placed at the beginning because they are only the unaffected tombstones)
def create_log_and_hint(tombstones:dict[str,str], merged_kv:dict, new_log_loc:Path, new_hint_loc:Path) -> bool:
    hints:dict[str,int] = {}
    for tombstone_key, tombstone_value in tombstones.items():
        store.process_delete(tombstone_key,new_log_loc,{})

    for key, value in merged_kv.items():
        store.process_put(key, value, new_log_loc, hints)

    for hint_key, hint_value in hints.items():
        store.process_put(hint_key, str(hint_value), new_hint_loc, {})

    return True

# swap Path names
def swap_names(new:Path,old:Path) -> bool:
    p = Path(new)
    p.rename(Path(old))
    return True

# remove the files from processed_files
# align the log ids of the new files
def remove_old_set_new(all_logs:list[tuple[Path,Path]], processed_files:list[Path], tmp_name:Path, tmp_hint_name:Path) -> bool:
    updated_all_logs = wal.remove_from_wal(processed_files, all_logs)
    new_name = wal.next_name(updated_all_logs, not_this=[tmp_name])
    swap_names(tmp_name, new_name)
    swap_names(tmp_hint_name, wal.new_hint_name(new_name))
    return True

# if org_type is "compact" then compact, else if org_type is "merge" then merged
def replace(all_logs:list[tuple[Path, Path]], directory, org_type, threshold=500) -> bool:
    processed_files = []
    if org_type == "compact":
        processed_files = wal.should_compact(all_logs)
    else:
        processed_files = wal.should_merge(all_logs, threshold)
    tmp_name = wal.next_name(all_logs)
    tmp_hint_name = wal.new_hint_name(tmp_name)

    create_log_and_hint(tombstones(processed_files),
                        merged_kv(processed_files),
                        tmp_name,
                        tmp_hint_name)
    return remove_old_set_new(all_logs,processed_files,tmp_name,tmp_hint_name)


# controller to execute background merge and compact functions
def compact_and_merge(every_x_sec:float, directory, threshold) -> bool:
    start_time = time.monotonic()
    counter = 0
    while True: #don't run all of the time, because that's unnecessary overhead
        files = wal.get_logs(directory)
        replace(files, "compact", threshold)
        if counter > 10:
            replace(files, "merge", threshold)
            counter = 0
        time.sleep(every_x_sec - ((time.monotonic() - start_time) % every_x_sec))

    return False
