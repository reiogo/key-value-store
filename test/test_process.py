from src.processer import *
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
    a1,k1,v1 = "PUT","hi-key","hello"
    a2,k2 = "GET","hi-key"
    d1 = recreate_hash('/usr/key-value/storage/test.txt')
    assert process(a1,k1,v1,d1,'/usr/key-value/storage/test.txt') == ""
    assert process(a2,k2,"",d1,'/usr/key-value/storage/test.txt') == "hello"

def test_process_put() -> None:
    o1 = process_put("t1", "two",'/usr/key-value/storage/test.txt')
    o2 = process_put("t2","",'/usr/key-value/storage/test.txt')
    o3 = process_put("","hi",'/usr/key-value/storage/test.txt')
    assert process_get("t1", '/usr/key-value/storage/test.txt',o1) == "two"
    assert process_get("t2", '/usr/key-value/storage/test.txt',o2) == ""
    assert process_get("", '/usr/key-value/storage/test.txt',o3) == ""


def test_process_get() -> None:
    assert process_get("one", '/usr/key-value/storage/test_rebuild.txt', 0) == "wrong"
    # assert process_get("hi-key", '/usr/key-value/storage/test.txt') == "hello"
    # assert process_get("test1", '/usr/key-value/storage/test.txt') == "correct"
