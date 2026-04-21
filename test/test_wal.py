import pytest
import os
from src.wal import *
from src.my_hash import recreate_hash
import src.store as store
from pathlib import Path
import time

def setup_test_log(l1:Path, h:dict):
    l1.unlink(missing_ok=True)
    # for key,value in h.items():
    #     store.process_put(key,value,l1,{})
    k1 = "hi"
    v1 = "whats"

    w1 = ((0).to_bytes(1, "big")
          + len(k1.encode("utf-8")).to_bytes(4, "big")
          + k1.encode("utf-8")
          + len(v1.encode("utf-8")).to_bytes(4, "big")
          + v1.encode("utf-8"))
    c1 = zlib.crc32(w1)
    p1 = (w1 + c1.to_bytes(4,"big"))
    o1 = offset(l1)
    # print(o1)
    # ==================
    k2 = "secondkey"
    v2 = "secondvalue"

    w2 = ((0).to_bytes(1, "big")
          + len(k2.encode("utf-8")).to_bytes(4, "big")
          + k2.encode("utf-8")
          + len(v2.encode("utf-8")).to_bytes(4, "big")
          + v2.encode("utf-8"))
    c2 = zlib.crc32(w2)
    p2 = (w2 + c2.to_bytes(4,"big"))
    o2 = offset(l1)
    # print(o2)

    assert wal_append(p1, l1) is True
    assert wal_append(p2, l1) is True


def test_offset() -> None:
    test_log = Path('/usr/key-value/test/test_storage/test_wal.bin')
    assert offset(test_log) == os.path.getsize(test_log)

    k1 = "hi"
    v1 = "whats"
    w1 = ((0).to_bytes(1, "big")
          + len(k1.encode("utf-8")).to_bytes(4, "big")
          + k1.encode("utf-8")
          + len(v1.encode("utf-8")).to_bytes(4, "big")
          + v1.encode("utf-8"))
    c1 = zlib.crc32(w1)
    p1 = (w1 + c1.to_bytes(4,"big"))

    assert wal_append(p1, test_log) is True
    assert offset(test_log) == os.path.getsize(test_log)

def test_wal_append() -> None:
    test_log = Path('/usr/key-value/test/test_storage/test_wal.bin')
    k1 = "hi"
    v1 = "whats"

    w1 = ((0).to_bytes(1, "big")
          + len(k1.encode("utf-8")).to_bytes(4, "big")
          + k1.encode("utf-8")
          + len(v1.encode("utf-8")).to_bytes(4, "big")
          + v1.encode("utf-8"))
    c1 = zlib.crc32(w1)
    p1 = (w1 + c1.to_bytes(4,"big"))
    o1 = offset(test_log)

    assert wal_append(p1, test_log) is True
    assert read(o1, test_log) == v1

def test_read_wal() -> None:
    test_log = Path('/usr/key-value/test/test_storage/test_wal.bin')
    setup_test_log(test_log, {"hi":"whats", "hello":"why"})
    o1 = 0
    c1,p1,k1,v1,o2 = read_wal(o1, test_log)
    assert c1 == True
    assert p1 == 0
    assert k1 == "hi"
    assert v1 == "whats"
    assert o2 == 20

    c2,p2,k2,v2,o3 = read_wal(o2, test_log)
    assert c2 == True
    assert p2 == 0
    assert k2 == "secondkey"
    assert v2 == "secondvalue"
    assert o3 == 53

def test_package_kv_put() -> None:
    k1 = "hi"
    v1 = "what"

    p1 = ((0).to_bytes(1,"big")
          + len(k1.encode("utf-8")).to_bytes(4, "big")
          + k1.encode("utf-8")
          + len(v1.encode("utf-8")).to_bytes(4, "big")
          + v1.encode("utf-8"))
    checksum = zlib.crc32(p1).to_bytes(4,"big")
    assert package_kv(k1,v1,False) == p1 + checksum

def test_package_kv_delete() -> None:
    k1 = "hi"
    v1 = ""
    p1 = ((1).to_bytes(1,"big")
          + len(k1.encode("utf-8")).to_bytes(4, "big")
          + k1.encode("utf-8")
          + len(v1.encode("utf-8")).to_bytes(4, "big")
          + v1.encode("utf-8"))
    checksum = zlib.crc32(p1).to_bytes(4,"big")
    assert package_kv(k1,v1,True) == p1 + checksum

def test_compact_wal() -> None:
    dir1 = Path('/usr/key-value/test/test_storage/test_wal')
    l1 = Path('/usr/key-value/test/test_storage/test_wal/active.bin')
    d1 = {'hi':38}
    d2 = {'hi':'4'}
    d3 = {'hi':4}
    d4 = {'del':""}

    l1.unlink(missing_ok=True)
    assert store.process(dir1,d1,"PUT","hi", "8") == "PUT succeeded"
    assert store.process(dir1,d1,"PUT","hi", "7") == "PUT succeeded"
    assert store.process(dir1,d1,"PUT","hi", "4") == "PUT succeeded"
    assert store.process(dir1,d1,"DELETE","del", "") == "DELETE succeeded"
    assert compactWal({},l1, "offset") == d1
    assert compactWal({},l1, "value") == d2
    assert compactWal({},l1, "value_as_int") == d3
    assert compactWal({},l1, "tombstones") == d4

def test_name_matches_hint() -> None:
    test_log = Path('/usr/key-value/test/test_storage/test_compaction/')
    test_hint = Path('/usr/key-value/test/test_storage/htest_compaction/')
    assert name_matches_hint(test_log, test_hint) is True

def test_next_name() -> None:
    l1 = Path('/usr/key-value/test/test_storage/1.bin')
    h1 = Path('/usr/key-value/test/test_storage/h1.bin')
    l2 = Path('/usr/key-value/test/test_storage/2.bin')
    h2 = Path('/usr/key-value/test/test_storage/h2.bin')
    next_log1 = Path('/usr/key-value/test/test_storage/3.bin')

    assert next_name([(l1,h1),(l2,h2)]) == next_log1

    l3 = Path('/usr/key-value/test/test_storage/300.bin')
    h3 = Path('/usr/key-value/test/test_storage/h300.bin')
    next_log2 = Path('/usr/key-value/test/test_storage/301.bin')
    assert next_name([(l1,h1),(l2,h2),(l3,h3)]) == next_log2

def test_new_hint_name() -> None:
    test_log = Path('/usr/key-value/test/test_storage/1.bin')
    test_hint = Path('/usr/key-value/test/test_storage/h1.bin')
    assert new_hint_name(test_log) ==  test_hint

def test_remove_from_wal() -> None:
    l1 = Path('/usr/key-value/test/test_storage/test_remove_from_wal/1.bin')
    l1.touch()
    h1 = Path('/usr/key-value/test/test_storage/test_remove_from_wal/h1.bin')
    h1.touch()
    l2 = Path('/usr/key-value/test/test_storage/test_remove_from_wal/2.bin')
    l2.touch()
    h2 = Path('/usr/key-value/test/test_storage/test_remove_from_wal/h2.bin')
    h2.touch()
    l3 = Path('/usr/key-value/test/test_storage/test_remove_from_wal/3.bin')
    l3.touch()
    h3 = Path('/usr/key-value/test/test_storage/test_remove_from_wal/h3.bin')
    h3.touch()
    assert remove_from_wal([l1,h1,l2,h2],[(l1,h1),(l2,h2),(l3,h3)]) == [(l3,h3)]
    assert not l1.exists()
    assert not h1.exists()
    assert not l2.exists()
    assert not h2.exists()
    assert l3.exists()
    assert h3.exists()
    l3.unlink()
    h3.unlink()


def test_should_compact() -> None:
    l1 = Path('/usr/key-value/test/test_storage/get_logs/1.bin')
    h1 = Path('/usr/key-value/test/test_storage/get_logs/h1.bin')
    l2 = Path('/usr/key-value/test/test_storage/get_logs/2.bin')
    h2 = Path('')

    f1 = [(l2, h2),(l1, h1)]
    f2 = [l2]
    assert should_compact(f1) == f2

def test_should_merge() -> None:
    l1 = Path('/usr/key-value/test/test_storage/get_logs/1.bin')
    h1 = Path('/usr/key-value/test/test_storage/get_logs/h1.bin')
    l2 = Path('/usr/key-value/test/test_storage/get_logs/2.bin')
    h2 = Path('')
    thresh = 200

    f1 = [(l2, h2),(l1, h1)]
    f2 = [l2,l1]
    assert should_merge(f1,thresh) == f2


def test_get_logs() -> None:
    d1 = Path('/usr/key-value/test/test_storage/get_logs')
    l1 = Path('/usr/key-value/test/test_storage/get_logs/1.bin')
    h1 = Path('/usr/key-value/test/test_storage/get_logs/h1.bin')
    l2 = Path('/usr/key-value/test/test_storage/get_logs/2.bin')
    h2 = Path('')
    a1 = Path('/usr/key-value/test/test_storage/active.bin')

    get_logs(d1) == [(l2,h2),(l1,h1)]





