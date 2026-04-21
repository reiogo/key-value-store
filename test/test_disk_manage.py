from src.disk_manage import *
import src.store as store
import pytest
from pathlib import Path
import src.wal as wal
import src.store as store


def test_merge_kvs() -> None:
    d1 = Path('/usr/key-value/test/test_storage/test_compaction/')
    l1 = Path('/usr/key-value/test/test_storage/test_compaction/1.bin')
    l2 = Path('/usr/key-value/test/test_storage/test_compaction/2.bin')
    f1 = [l1,l2]

    l1.unlink(missing_ok=True)
    l2.unlink(missing_ok=True)
    store.process_put("hi", "what",l1,{})
    store.process_put("hi", "excuse me",l1,{})
    store.process_put("excalibur", "excuse me",l1,{})
    store.process_put("hello", "donatello",l2,{})
    store.process_put("hello", "domingo",l2,{})
    store.process_put("excalibur", "excaliwhat",l2,{})

    assert merged_kv(f1) == {"hi":"excuse me",
                             "hello":"domingo",
                             "excalibur":"excaliwhat"}

def test_create_log_and_hint() -> None:
    test_log = Path('/usr/key-value/test/test_storage/test_compaction/new_file.bin')
    test_hint = Path('/usr/key-value/test/test_storage/test_compaction/new_file_hint.bin')
    test_log.unlink(missing_ok= True) #clearing past entries of new_file
    test_hint.unlink(missing_ok= True) #clearing past entries of new_file_hint

    k1 = {'hi': 'what'}
    t1 = {'hello':""}
    h1 = {'hi': '18'}
    assert create_log_and_hint(t1, k1, test_log, test_hint) is True
    assert wal.compactWal({}, test_log, "value") == k1
    assert wal.compactWal({}, test_log, "tombstones") == t1
    assert wal.compactWal({}, test_hint, "value") == h1

def test_remove_old_set_new() -> None:
    d1 = Path('/usr/key-value/test/test_storage/test_remove_old_set_new/')
    for child in d1.iterdir():
        child.unlink(missing_ok=True)

    l1 = Path('/usr/key-value/test/test_storage/test_remove_old_set_new/1.bin')
    l1.touch()
    h1 = Path('/usr/key-value/test/test_storage/test_remove_old_set_new/h1.bin')
    h1.touch()
    l2 = Path('/usr/key-value/test/test_storage/test_remove_old_set_new/2.bin')
    l2.touch()
    h2 = Path('/usr/key-value/test/test_storage/test_remove_old_set_new/h2.bin')
    h2.touch()
    l3 = Path('/usr/key-value/test/test_storage/test_remove_old_set_new/300.bin')
    with l3.open("ab") as file:
        file.write("hi".encode("utf-8"))
    h3 = Path('/usr/key-value/test/test_storage/test_remove_old_set_new/h300.bin')
    with h3.open("ab") as file:
        file.write("hi_hint".encode("utf-8"))
    all1 = [(l1,h1),(l2,h2),(l3,h3)]
    proc1 = [l2]

    assert remove_old_set_new(all1,proc1,l3,h3) is True

    with l2.open("rb") as file:
        new_log = file.readline()
    assert new_log.decode("utf-8") == "hi"

    with h2.open("rb") as file:
        new_hint = file.readline()
    assert new_hint.decode("utf-8") == "hi_hint"

def test_tomb_stone() -> None:
    l1 = Path('/usr/key-value/test/test_storage/test_compaction/1.bin')
    l2 = Path('/usr/key-value/test/test_storage/test_compaction/2.bin')
    f1 = [l1,l2]

    l1.unlink(missing_ok=True)
    l2.unlink(missing_ok=True)
    store.process_put("hi", "what",l1,{})
    store.process_put("hi", "excuse me",l1,{})
    store.process_put("excalibur", "excuse me",l1,{})
    store.process_delete("excalibur",l1,{})
    store.process_put("hello", "donatello",l2,{})
    store.process_put("hello", "domingo",l2,{})
    store.process_delete("hello",l1,{})
    store.process_put("excalibur", "excaliwhat",l2,{})

    assert tombstones(f1) == {"excalibur":"", "hello":""}
