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
    assert process(a1,k1,v1) == ""
    assert process(a2,k2,"") == "hello"

def test_put_process() -> None:
    put_process("one", "two")
    assert get_process("one") == "two"


def test_get_process() -> None:
    # wrote it in already
    assert get_process("two") == "one"
