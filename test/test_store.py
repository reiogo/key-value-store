from src.store import *
import pytest
from src.my_hash import recreate_hash
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

