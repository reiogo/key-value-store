from src.processer import *
import pytest
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
    assert process(a1,k1,v1,'/usr/key-value/storage/test.txt') == ""
    assert process(a2,k2,"",'/usr/key-value/storage/test.txt') == "hello"

def test_put_process() -> None:
    put_process("t1", "two",'/usr/key-value/storage/test.txt')
    put_process("t2","",'/usr/key-value/storage/test.txt')
    put_process("","hi",'/usr/key-value/storage/test.txt')
    assert get_process("t1", '/usr/key-value/storage/test.txt') == "two"
    assert get_process("t2", '/usr/key-value/storage/test.txt') == ""
    assert get_process("", '/usr/key-value/storage/test.txt') == ""


def test_get_process() -> None:
    # wrote it in already
    assert get_process("test2", '/usr/key-value/storage/test.txt') == ""
    assert get_process("hi-key", '/usr/key-value/storage/test.txt') == "hello"
    assert get_process("test1", '/usr/key-value/storage/test.txt') == "correct"
