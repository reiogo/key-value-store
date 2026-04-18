import pytest
import os
from src.wal import *
from src.my_hash import recreate_hash

def test_offset() -> None:
     test_url = '/usr/key-value/storage/test_wal.bin'
     assert offset(test_url) == os.path.getsize(test_url)

def test_append() -> None:
    test_url = '/usr/key-value/storage/test_wal.bin'
    k1 = "hi"
    v1 = "whats"

    w1 = ((0).to_bytes(1, "big")
          + len(k1.encode("utf-8")).to_bytes(4, "big")
          + k1.encode("utf-8")
          + len(v1.encode("utf-8")).to_bytes(4, "big")
          + v1.encode("utf-8"))
    c1 = zlib.crc32(w1)
    p1 = (w1 + c1.to_bytes(4,"big"))
    o1 = offset(test_url)

    assert append(p1, test_url) is True
    assert read(o1, test_url) == v1

def test_read() -> None:
    test_url = '/usr/key-value/storage/test_wal.bin'
    o1 = 0
    r1 = "whats"
    assert read(o1, test_url) == r1

def test_read_wal() -> None:
    test_url = '/usr/key-value/storage/test_wal.bin'
    o1 = 0
    c1,p1,k1,v1,o2 = read_wal(o1, test_url)
    assert c1 == True
    assert p1 == 0
    assert k1 == "hi"
    assert v1 == "whats"
    assert o2 == 15



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
