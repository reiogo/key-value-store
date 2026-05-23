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

    assert wal_append(p1, l1) == os.path.getsize(l1)
    assert wal_append(p2, l1) == os.path.getsize(l1)


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

    assert wal_append(p1, l1) == os.path.getsize(l1)
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

    assert wal_append(p1, l1) == os.path.getsize(l1)
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

def _put_helper(key, val, l1, h1):
    wal_append(package_kv(key, val),l1)
    wal_append(package_hint_kv(key, offset(h1)),h1)

def _build_helper(d1,a1,l1,h1) -> dict[str,int]:
    imh = {}

    a1.unlink(missing_ok=True)
    a1.touch()
    l1.unlink(missing_ok=True)
    l1.touch()
    h1.unlink(missing_ok=True)
    h1.touch()
    store.put("hi", "what",d1,imh,100)
    store.put("hi", "excuse me",d1,imh,100)
    store.put("excalibur", "excuse me",d1,imh,100)
    store.remove("excalibur",d1,imh)
    _put_helper("hello", "donatello", l1, h1)
    _put_helper("cat", "truffle", l1, h1)
    wal_append(package_kv("hello", "domingo",0),l1)
    # wal_append(package_hint_kv("hello", 14),h1)
    wal_append(package_kv("hello","",package_type=1), l1)
    wal_append(package_kv("cat", "flamingo",0),l1)
    # wal_append(package_hint_kv("hello", 14),h1)
    wal_append(package_kv("cat","",package_type=1), l1)
    _put_helper("cat", "truffle2", l1, h1)
    _put_helper("excalibur", "excaliwhat", l1, h1)
    _put_helper("excalibur", "dolma", l1, h1)
    _put_helper("dancing", "tiger", l1, h1)
    return imh

def test_create_hash() -> None:
    d1 = test_dir / 'create_hash'
    d1.mkdir(exist_ok=True)
    a1 = d1 / 'active.bin'
    l1 = d1 / '1.bin'
    h1 = d1 / 'h1.bin'
    _build_helper(d1,a1,l1,h1)
    hsh_offsets = {}
    hsh_offsets = create_hash(hsh_offsets,l1, "offsets")
    assert(hsh_offsets == {
        "cat":133,
        "excalibur":189,
        "dancing":216})
    hsh_offsets = create_hash(hsh_offsets,a1, "offsets")
    assert(hsh_offsets == {"hi":19,
                   "dancing": 216 ,
                   "cat":133})

    hsh_values = {}
    hsh_values = create_hash(hsh_values,l1, "values")
    assert(hsh_values == {
        "cat":"truffle2",
        "excalibur":"dolma",
        "dancing":"tiger"})
    hsh_values = create_hash(hsh_values,a1, "values")
    assert(hsh_values == {"hi":"excuse me",
                   "dancing": "tiger" ,
                   "cat":"truffle2"})


def test_create_tombstones() -> None:
    d1 = test_dir / 'create_tombstones'
    d1.mkdir(exist_ok=True)
    a1 = d1 / 'active.bin'
    l1 = d1 / '1.bin'
    h1 = d1 / 'h1.bin'
    _build_helper(d1,a1,l1,h1)
    hsh = {}
    hsh = create_tombstones(hsh, l1)
    assert(hsh == {"hello": "" })


def test_package_hint_kv() -> None:
    k1 = "hi"
    v1 = "0"
    b1 = (len(k1.encode("utf-8")).to_bytes(4, "big")
          + k1.encode("utf-8")
          + len(v1.encode("utf-8")).to_bytes(4, "big")
          + v1.encode("utf-8"))

    assert (package_hint_kv("hi", 0) == b1)

def test_read_hint_file() -> None:
    d1 = test_dir / 'read_hint_file'
    d1.mkdir(exist_ok=True)
    h1 = d1 / 'h1.bin'
    h1.unlink(missing_ok=True)
    h1.touch()

    hashmap = {"hi": 0}
    wal_append(package_hint_kv("hi", 0), h1)
    assert(read_hint_file(h1) == hashmap)
    hashmap = {"hi": 0, "hi2": 11}
    wal_append(package_hint_kv("hi2", 11), h1)
    assert(read_hint_file(h1) == hashmap)








