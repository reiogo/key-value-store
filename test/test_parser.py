from src.parser import *
import pytest

def test_parser_put() -> None:
    s1 = b"PUT hi hello"
    s2 = b"PUT hi "
    s3 = b"PUT"

    assert parser(s1) == ("PUT", "hi", "hello")
    assert parser(s2) == ("PUT", "hi", "")
    assert parser(s3) == ("PUT", "", "")

def test_parser_get() -> None:
    s1 = b"GET hi"
    s2 = b"GET"
    assert parser(s1) == ("GET", "hi", "")
    assert parser(s2) == ("GET", "", "")

def test_parser_get() -> None:
    s1 = b"DELETE hi"
    s2 = b"DELETE"
    assert parser(s1) == ("DELETE", "hi", "")
    assert parser(s2) == ("DELETE", "", "")
