from src.my_hash import *
import pytest

def test_recreate_hash() -> None:
    d1 = {}
    test_url = '/usr/key-value/storage/test_rebuild.bin'
    d1['hi'] = 60

    assert recreate_hash(test_url) == d1


def test_get_offset() -> None:
    k1 = "hi"
    d1 = {}
    d1[k1] = 10
    assert get_offset(k1, d1) == 10
    assert get_offset("hello", d1) == -1 # if not in hash

def test_update() -> None:
    k1 = "hi"
    d1 = {}
    d1[k1] = 10

    o1 = 25334
    update(k1,o1,d1)
    assert get_offset(k1, d1) == o1
