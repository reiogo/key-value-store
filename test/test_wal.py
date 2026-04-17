import pytest
import os
from src.wal import *
from src.my_hash import recreate_hash

def test_offset() -> None:
     test_url = '/usr/key-value/storage/test.bin'
     assert offset(test_url) == os.path.getsize(test_url)

def test_append() -> None:
    test_url = '/usr/key-value/storage/test.bin'
    k1 = "hi"
    v1 = "whats"

    w1 = (len(k1.encode("utf-8")).to_bytes(4, "big")
          + k1.encode("utf-8")
          + len(v1.encode("utf-8")).to_bytes(4, "big")
          + v1.encode("utf-8"))
    o1 = offset(test_url)

    assert append(w1, test_url) is True
    assert read(o1, test_url) == v1

def test_read() -> None:
    test_url = '/usr/key-value/storage/test.bin'
    o1 = 0
    r1 = "whats"
    assert read(o1, test_url) == r1
