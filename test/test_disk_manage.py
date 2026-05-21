from src.disk_manage import *
import src.store as store
import pytest
from pathlib import Path
import src.wal as wal
import src.store as store

test_dir = Path('/usr/key-value/test/test_storage/disk_manage')
test_dir.mkdir(parents=True, exist_ok=True)

def test_merge_kvs() -> None:
    d1 = test_dir / 'merge_kvs'
    d1.mkdir(exist_ok=True)
    l1 = d1 / '1.bin'
    l2 = d1 / '2.bin'
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
    d1 = test_dir / 'create_log_and_hint'
    d1.mkdir(exist_ok=True)
    l1 = d1 / 'new_file.bin'
    h1 = d1 / 'new_file_hint.bin'

    l1.unlink(missing_ok= True) #clearing past entries of new_file
    h1.unlink(missing_ok= True) #clearing past entries of new_file_hint

    k1 = {'hi': 'what'}
    t1 = {'hello':""}
    hi1 = {'hi': '18'}
    assert create_log_and_hint(t1, k1, l1, h1) is True
    assert wal.compactWal({}, l1, "value") == k1
    assert wal.compactWal({}, l1, "tombstones") == t1
    assert wal.compactWal({}, h1, "value") == hi1

def test_remove_old_set_new() -> None:
    d1 = test_dir / 'remove_old_set_new'
    d1.mkdir(exist_ok=True)

    for child in d1.iterdir():
        child.unlink(missing_ok=True)
    l1 = d1 / '1.bin'
    l1.touch()
    h1 = d1 / 'h1.bin'
    h1.touch()

    l2 = d1 / '2.bin'
    l2.touch()
    h2 = d1 / 'h2.bin'
    h2.touch()

    l3 = d1 / '300.bin'
    with l3.open("ab") as file:
        file.write("hi".encode("utf-8"))
    h3 = d1 / 'h300.bin'
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
    d1 = test_dir / 'tomb_stone'
    d1.mkdir(exist_ok=True)
    l1 = d1 / '1.bin'
    l2 = d1 / '2.bin'

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
