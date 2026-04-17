from src.store import *
import pytest
from src.my_hash import recreate_hash
def test_parser() -> None:
    s1 = b"PUT hi hello"
    s2 = b"PUT hi "
    s3 = b"PUT"

    s4 = b"GET hi"
    s5 = b"GET"
    assert parser(s1) == ("PUT", "hi", "hello")
    assert parser(s2) == ("PUT", "hi", "")
    assert parser(s3) == ("PUT", "", "")
    assert parser(s4) == ("GET", "hi", "")
    assert parser(s5) == ("GET", "", "")

def test_process() -> None:
    test_url = '/usr/key-value/storage/test.bin'
    a1,k1,v1 = "PUT","hi-key","hello"
    a2,k2 = "GET","hi-key"
    a3,k3 = "GET","doesn't exist"
    a4,k4 = "GE","doesn't exist"

    d1 = recreate_hash(test_url)
    assert process(a1,k1,v1,d1,test_url) == "PUT succeeded"
    assert process(a2,k2,"",d1,test_url) == "hello"
    assert process(a3,k3,"",d1,test_url) == "GET failed"
    assert process(a4,k4,"",d1,test_url) == "Parse failed"

def test_process_put() -> None:
    k1 = "hi"
    v1 = "whats"

    a1 = (len(k1.encode("utf-8")).to_bytes(4, "big")
          + k1.encode("utf-8")
          + len(v1.encode("utf-8")).to_bytes(4, "big")
          + v1.encode("utf-8"))
    assert process_put(k1,v1) == a1
