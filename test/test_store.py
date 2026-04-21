from src.store import *
import pytest
from src.my_hash import recreate_hash
import zlib
from pathlib import Path

def test_search() -> None:
    pass

def test_process() -> None:
    active = Path('/usr/key-value/test/test_storage/test_process/active.bin')
    active.unlink()

    test_log = Path('/usr/key-value/test/test_storage/test_process/')
    a1,k1,v1 = "PUT","hi-key","hello"
    a2,k2 = "GET","hi-key"
    a3,k3 = "GET","doesn't exist"
    a4,k4 = "GE","doesn't exist"
    a5,k5,v5 = "PUT","bonjour","ca va?"
    a6,k6 = "GET","bonjour"
    a7,k7,v7 = "PUT","hi-key","bye"
    a8,k8 = "GET","hi-key"

    d1 = recreate_hash(test_log)
    assert process(test_log,d1,a1,k1,v1) == "PUT succeeded"
    assert process(test_log,d1,a2,k2) == "hello"
    assert process(test_log,d1,a3,k3) == "GET failed"
    assert process(test_log,d1,a4,k4) == "Error"
    assert process(test_log,d1,a5,k5,v5) == "PUT succeeded"
    assert process(test_log,d1,a6,k6) == "ca va?"
    assert process(test_log,d1,a7,k7,v7) == "PUT succeeded"
    assert process(test_log,d1,a8,k8) == "bye"

# def test_process_delete() -> None:
#     active = Path('/usr/key-value/test/test_storage/test_process/active.bin')
#     active.unlink()
#     test_log = Path('/usr/key-value/test/test_storage/test_process/')
#     a1,k1,v1 = "PUT","hi-key","hello"
#     a2,k2 = "DELETE","hi-key",
#     a3,k3 = "GET","hi-key"

#     d1 = recreate_hash(test_log)
#     assert process(test_log,d1,a1,k1,v1) == "PUT succeeded"
#     assert process(test_log,d1,a3,k3) == v1
#     assert process(test_log,d1,a2,k2,"") == "DELETE succeeded"
#     assert process(test_log,d1,a3,k3) == "GET failed"

