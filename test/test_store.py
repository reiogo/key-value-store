from src.store import *
import pytest
from src.my_hash import recreate_hash
import src.wal as wal
import zlib
from pathlib import Path

test_dir = Path('/usr/key-value/test/test_storage/store')
test_dir.mkdir(parents=True, exist_ok=True)

def test_process() -> None:
    d1 = test_dir / 'process'
    d1.mkdir(exist_ok=True)
    l1 = d1 / 'active.bin'
    l1.unlink(missing_ok=True)

    a1,k1,v1 = "PUT","hi-key","hello"
    a2,k2 = "GET","hi-key"
    a3,k3 = "GET","doesn't exist"
    a4,k4 = "GE","doesn't exist"
    a5,k5,v5 = "PUT","bonjour","ca va?"
    a6,k6 = "GET","bonjour"
    a7,k7,v7 = "PUT","hi-key","bye"
    a8,k8 = "GET","hi-key"

    dict1 = recreate_hash(d1)
    assert process(d1,dict1,a1,k1,v1) == "PUT succeeded"
    assert process(d1,dict1,a2,k2) == "hello"
    assert process(d1,dict1,a3,k3) == "GET failed"
    assert process(d1,dict1,a4,k4) == "Error"
    assert process(d1,dict1,a5,k5,v5) == "PUT succeeded"
    assert process(d1,dict1,a6,k6) == "ca va?"
    assert process(d1,dict1,a7,k7,v7) == "PUT succeeded"
    assert process(d1,dict1,a8,k8) == "bye"

def test_fetch() -> None:
    d1 = test_dir / 'fetch'
    d1.mkdir(exist_ok=True)
    a1 = d1 / 'active.bin'
    a1.unlink()
    a1.touch()
    l1 = d1 / '1.bin'
    l1.touch()
    h1 = d1 / 'h1.bin'
    h1.touch()

    imh = {}
    put("hi", "bye", d1, imh, 100)
    wal.wal_append(wal.package_kv("yellow", "submarine",0),l1)
    wal.wal_append(wal.package_hint_kv("yellow", 0),h1)
    assert(fetch("yellow",d1,imh) == "submarine")
    assert(fetch("hi",d1,imh) == "bye")
    assert(fetch("hat",d1,imh) == "")


def test_put() -> None:
    d1 = test_dir / 'put'
    d1.mkdir(exist_ok=True)
    a1 = d1 / 'active.bin'
    a1.unlink(missing_ok=True)
    a1.touch()
    l1 = d1 / '1.bin'
    l1.unlink(missing_ok=True)
    imh = {}

    put("tom", "cat", d1, imh, 0)
    assert(imh == {})
    assert(l1.exists())
    assert(wal.read_wal(0,l1) == (True, 0, "tom", "cat", 19))
    put("hi", "bye", d1, imh, 100)
    assert(imh == {"hi": 0})
    assert(wal.read_wal(0,a1) == (True, 0, "hi", "bye", 18))
    put("hello", "bello", d1, imh, 100)
    assert(imh == {"hello": 18, "hi" : 0})
    assert(wal.read_wal(18,a1) == (True, 0, "hello", "bello", 41))


def test_put_helper() -> None:
    d1 = test_dir / 'put_helper'
    d1.mkdir(exist_ok=True)
    l1 = d1 / '1.bin'
    l1.unlink(missing_ok=True)
    l1.touch()

    put_helper("hi", "bye", l1)
    assert(wal.read_wal(0,l1) == (True, 0, "hi", "bye", 18))
    put_helper("hello", "bello", l1)
    assert(wal.read_wal(18,l1) == (True, 0, "hello", "bello", 41))


