from src.store import *
import pytest
from src.my_hash import recreate_hash
import zlib

def test_process_put() -> None:
    test_url = '/usr/key-value/storage/test_store.py'
    a1,k1,v1 = "PUT","hi-key","hello"

    d1 = recreate_hash(test_url)
    assert process(test_url,d1,a1,k1,v1) == "PUT succeeded"

def test_process_get() -> None:
    test_url = '/usr/key-value/storage/test_store.py'
    a1,k1,v1 = "PUT","hi-key","hello"
    a2,k2 = "GET","hi-key"
    a3,k3 = "GET","doesn't exist"
    a4,k4 = "GE","doesn't exist"

    d1 = recreate_hash(test_url)
    assert process(test_url,d1,a1,k1,v1) == "PUT succeeded"
    assert process(test_url,d1,a2,k2) == "hello"
    assert process(test_url,d1,a3,k3) == "GET failed"
    assert process(test_url,d1,a4,k4) == "Parse failed"

def test_process_delete() -> None:
    test_url = '/usr/key-value/storage/test_store.py'
    a1,k1,v1 = "PUT","hi-key","hello"
    a2,k2 = "DELETE","hi-key",
    a3,k3 = "GET","hi-key"

    d1 = recreate_hash(test_url)
    #assert process(test_url,d1,a1,k1,v1) == "PUT succeeded"
    assert process(test_url,d1,a2,k2,"") == "DELETE succeeded"
    assert process(test_url,d1,a3,k3) == "GET failed"

