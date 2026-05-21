import pytest
import os
from src.wal import *
from src.my_hash import recreate_hash
import src.store as store
from pathlib import Path
import time

test_dir = Path('/usr/key-value/test/test_storage/wal')
test_dir.mkdir(parents=True, exist_ok=True)

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
    d1 = test_dir / 'offset'
    d1.mkdir(exist_ok=True)
    l1 = d1 / '1.bin'

    assert offset(l1) == os.path.getsize(l1)

    k1 = "hi"
    v1 = "whats"
    w1 = ((0).to_bytes(1, "big")
          + len(k1.encode("utf-8")).to_bytes(4, "big")
          + k1.encode("utf-8")
          + len(v1.encode("utf-8")).to_bytes(4, "big")
          + v1.encode("utf-8"))
    c1 = zlib.crc32(w1)
    p1 = (w1 + c1.to_bytes(4,"big"))

    assert wal_append(p1, l1) is True
    assert offset(l1) == os.path.getsize(l1)

def test_wal_append() -> None:
    d1 = test_dir / 'wal_append'
    d1.mkdir(exist_ok=True)
    l1 = d1 / '1.bin'

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

    assert wal_append(p1, l1) is True
    assert read(o1, l1) == v1

def test_read_wal() -> None:
    d1 = test_dir / 'read_wal'
    d1.mkdir(exist_ok=True)
    l1 = d1 / '1.bin'

    setup_test_log(l1, {"hi":"whats", "hello":"why"})
    o1 = 0
    c1,p1,k1,v1,o2 = read_wal(o1, l1)
    assert c1 == True
    assert p1 == 0
    assert k1 == "hi"
    assert v1 == "whats"
    assert o2 == 20

    c2,p2,k2,v2,o3 = read_wal(o2, l1)
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
    d1 = test_dir / 'compact_wal'
    d1.mkdir(exist_ok=True)
    l1 = d1 / 'active.bin'

    dict1 = {'hi':38}
    dict2 = {'hi':'4'}
    dict3 = {'hi':4}
    dict4 = {'del':""}

    l1.unlink(missing_ok=True)
    assert store.process(d1,dict1,"PUT","hi", "8") == "PUT succeeded"
    assert store.process(d1,dict1,"PUT","hi", "7") == "PUT succeeded"
    assert store.process(d1,dict1,"PUT","hi", "4") == "PUT succeeded"
    assert store.process(d1,dict1,"DELETE","del", "") == "DELETE succeeded"
    assert compactWal({},l1, "offset") == dict1
    assert compactWal({},l1, "value") == dict2
    assert compactWal({},l1, "value_as_int") == dict3
    assert compactWal({},l1, "tombstones") == dict4

def test_name_matches_hint() -> None:
    d1 = test_dir / 'name_matches_hint'
    d1.mkdir(exist_ok=True)
    l1 = d1 / '1.bin'
    h1 = d1 / 'h1.bin'

    assert name_matches_hint(l1, h1) is True

# def test_next_name() -> None:
#     d1 = test_dir / 'next_name'
#     d1.mkdir(exist_ok=True)
#     l1 = d1 / '1.bin'
#     l2 = d1 / '2.bin'
#     l3 = d1 / '3.bin'
#     l300 = d1 / '300.bin'
#     l301 = d1 / '301.bin'

#     h1 = d1 / 'h1.bin'
#     h2 = d1 / 'h2.bin'
#     h300 = d1 / 'h300.bin'

#     assert next_name([(l1,h1),(l2,h2)]) == l3

#     assert next_name([(l1,h1),(l2,h2),(l300,h300)]) == l301

# def test_new_hint_name() -> None:
#     d1 = test_dir / 'new_hint_name'
#     d1.mkdir(exist_ok=True)
#     l1 = d1 / '1.bin'
#     h1 = d1 / 'h1.bin'

#     assert new_hint_name(l1) == h1

def test_should_compact() -> None:
    d1 = test_dir / 'should_compact'
    d1.mkdir(exist_ok=True)

    l1 = d1 / '1.bin'
    l2 = d1 / '2.bin'

    h1 = d1 / 'h1.bin'
    h2 = Path('')

    f1 = [(l2, h2),(l1, h1)]
    f2 = [l2]
    assert should_compact(f1) == f2

def test_should_merge() -> None:
    d1 = test_dir / 'should_merge'
    d1.mkdir(exist_ok=True)
    l1 = d1 / '1.bin'
    l1.touch()
    l2 = d1 / '2.bin'
    l2.touch()
    h1 = d1 / 'h1.bin'
    h1.touch()
    h2 = Path('')

    thresh = 200

    f1 = [(l1, h1),(l2, h2)]
    f2 = [l2,l1]
    assert should_merge(f1,thresh) == f2







