from src.process import *
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
