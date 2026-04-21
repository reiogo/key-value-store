from src.my_hash import *
import src.store as store
import pytest

def test_recreate_hash() -> None:
    dir1 = Path('/usr/key-value/test/test_storage/recreate_hash/')
    test_log = Path('/usr/key-value/test/test_storage/recreate_hash/active.bin')
    test_log.unlink(missing_ok=True)
    test_log.touch()
    d1 = {'hi':0}

    store.process_put("hi", "what", test_log,{})
    assert recreate_hash(dir1) == d1


def test_get_offset() -> None:
    k1 = "hi"
    d1 = {k1:10}
    assert get_offset(k1, d1) == 10
    assert get_offset("hello", d1) == -1 # if not in hash

def test_update() -> None:
    k1 = "hi"
    d1 = {k1:10}

    o1 = 25334
    update(k1,o1,d1)
    assert get_offset(k1, d1) == o1

def test_delete() -> None:
    k1 = "hi"
    d1 = {k1:10}

    assert delete(k1, d1) is True
    assert delete("doesn't exist", d1) is False
    assert d1.get("hi", "doesn't exist") == "doesn't exist"
