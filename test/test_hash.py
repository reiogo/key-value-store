from src.my_hash import *
import pytest

def test_recreate_hash() -> None:
    d1 = {}
    d1['one'] = 44
    d1['hi-key'] = 31
    d1['key'] = 52
    d1['test1'] = 74
    d1['t1'] = 88

    assert recreate_hash('/usr/key-value/storage/test_rebuild.txt') == d1


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
