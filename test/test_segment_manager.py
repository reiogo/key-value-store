from src.segment_manager import *
import src.store as store
import pytest
from pathlib import Path
import src.wal as wal
import src.store as store
test_dir = Path('/usr/key-value/test/test_storage/segment_manager')
test_dir.mkdir(parents=True, exist_ok=True)

def test_name_matches_hint() -> None:
    d1 = test_dir / 'name_matches_hint'
    l1 = d1 / '1.bin'
    h1 = d1 / 'h1.bin'

    assert name_matches_hint(l1, h1) is True

def test_log_id() -> None:
    d1 = test_dir / 'log_id'
    l1 = d1 / '1.bin'
    l2 = d1 / '2.bin'
    l50000 = d1 / '50000.bin'
    assert(log_id(l1) == 1)
    assert(log_id(l2) == 2)
    assert(log_id(l50000) == 50000)

def _put_helper(key, val, l1, h1):
    wal.wal_append(wal.package_kv(key, val),l1)
    wal.wal_append(wal.package_hint_kv(key, wal.offset(h1)),h1)

def test_tombstone() -> None:
    d1 = test_dir / 'tombstone'
    d1.mkdir(exist_ok=True)
    a1 = d1 / 'active.bin'
    l1 = d1 / '1.bin'
    h1 = d1 / 'h1.bin'
    imh = {}

    f1 = [l1,a1]

    l1.unlink(missing_ok=True)
    l1.touch()
    h1.unlink(missing_ok=True)
    h1.touch()
    store.put("hi", "what",d1,imh)
    store.put("hi", "excuse me",d1,imh)
    store.put("excalibur", "excuse me",d1,imh)
    store.remove("excalibur",d1,imh)
    _put_helper("hello", "donatello", l1, h1)
    wal.wal_append(wal.package_kv("hello", "domingo",0),l1)
    # wal.wal_append(wal.package_hint_kv("hello", 14),h1)
    wal.wal_append(wal.package_kv("hello","",package_type=1), l1)
    _put_helper("excalibur", "excaliwhat", l1, h1)

    assert tombstones(f1) == {"excalibur":"", "hello":""}


def test_merge_kvs() -> None:
    d1 = test_dir / 'merged_kv'
    d1.mkdir(exist_ok=True)
    a1 = d1 / 'active.bin'
    l1 = d1 / '1.bin'
    h1 = d1 / 'h1.bin'
    l2 = d1 / '2.bin'
    h2 = d1 / 'h2.bin'
    imh = {}
    f1 = [a1,l1,l2]

    a1.unlink(missing_ok=True)
    a1.touch()
    l1.unlink(missing_ok=True)
    l1.touch()
    h1.unlink(missing_ok=True)
    h1.touch()
    l2.unlink(missing_ok=True)
    l2.touch()
    h2.unlink(missing_ok=True)
    h2.touch()

    _put_helper("hi", "what", l1, h1)
    wal.wal_append(wal.package_kv("hello", "domingo",wal.offset(l1)),l1)
    # wal.wal_append(wal.package_hint_kv("hello", wal.offset(h1)),h1)
    wal.wal_append(wal.package_kv("hello","",package_type=1), l1)
    _put_helper("hi", "excuse me", l1, h1)
    _put_helper("excalibur", "excuse me",l1, h1)
    _put_helper("hello", "donatello", l2, h2)
    _put_helper("hello", "domingo", l2, h2)
    _put_helper("excalibur", "excaliwhat",l2, h2)

    assert merged_kv(f1) == {"hi":"excuse me",
                             "hello": "domingo",
                             "excalibur":"excaliwhat"}

def test_create_hint_file() -> None:
    d1 = test_dir / 'create_hint_file'
    d1.mkdir(exist_ok=True)
    l1 = d1 / '1.bin'
    h1 = d1 / 'h1.bin'
    h1.unlink(missing_ok=True)

    hints = {"hi":0}
    create_hint_file(hints,l1)

    assert (h1.exists())
    assert (wal.read_hint_file(h1) == hints)



def test_create_log_and_hint() -> None:
    d1 = test_dir / 'create_log_and_hint'
    d1.mkdir(exist_ok=True)
    a1 = d1 / "active.bin"
    l1 = d1 / 'new_file.bin'
    h1 = d1 / 'hnew_file.bin'

    a1.unlink(missing_ok= True)
    a1.touch()
    l1.unlink(missing_ok= True)
    h1.unlink(missing_ok= True)

    k1 = {'hi': 'what'}
    tomb1 = {'hello':""}
    hi1 = {'hi': 37}
    assert create_log_and_hint(tomb1, k1, l1) is True
    assert wal.create_hash({}, l1, "values") == k1
    assert wal.create_tombstones({}, l1) == tomb1
    assert wal.read_hint_file(h1) == hi1

def test_remove_old_set_new() -> None:
    d1 = test_dir / 'remove_old_set_new'
    d1.mkdir(exist_ok=True)

    for child in d1.iterdir():
        child.unlink(missing_ok=True)

    l1 = d1 / '1.bin'
    l1.touch()
    h1 = d1 / 'h1.bin'
    h1.touch()
    l2 = d1 / '2.bin'
    l2.touch()
    h2 = d1 / 'h2.bin'
    h2.touch()
    l3 = d1 / '3.bin'
    l3.touch()
    h3 = d1 / 'h3.bin'
    h3.touch()
    t1 = d1 / 't1.bin'
    t1.touch()
    ht1 = d1 / 'ht1.bin'
    ht1.touch()

    remove_old_set_new([l1,h1,l2,h2], l1, t1)
    assert l1.exists()
    assert h1.exists()
    assert not l2.exists()
    assert not h2.exists()
    assert l3.exists()
    assert h3.exists()

def  test_replace():
    d1 = test_dir / 'replace'
    d1.mkdir(exist_ok=True)
    l1 = d1 / '1.bin'
    l2 = d1 / '2.bin'


def test_remove() -> None:
    d1 = test_dir / 'remove'
    d1.mkdir(exist_ok=True)

    l1 = d1 / '1.bin'
    l1.touch(exist_ok=True)
    l2 = d1 / '2.bin'
    l2.touch(exist_ok=True)
    l3 = d1 / '3.bin'
    l3.touch(exist_ok=True)

    h1 = d1 / 'h1.bin'
    h1.touch(exist_ok=True)
    h2 = d1 / 'h2.bin'
    h2.touch(exist_ok=True)

    remove([l1,h1,l2,h2])
    assert not l1.exists()
    assert not l2.exists()
    assert not h1.exists()
    assert not h2.exists()
    assert get_segments(d1) == [(l3,Path(""))]

# def test_get_files() -> None:
#     d1 = test_dir / 'get_files'
#     d1.mkdir(exist_ok=True)
#     l1 = d1 / '1.bin'
#     l1.touch(exist_ok=True)
#     l2 = d1 / '2.bin'
#     l2.touch(exist_ok=True)
#     h1 = d1 / 'h1.bin'
#     h1.touch(exist_ok=True)
#     a1 = d1 / 'active.bin'
#     a1.touch(exist_ok=True)


#     assert (get_files(d1) == [l1,l2,a1,h1])

def test_get_segments() -> None:
    d1 = test_dir / 'get_segments'
    d1.mkdir(exist_ok=True)
    l1 = d1 / '1.bin'
    l1.touch()
    l2 = d1 / '2.bin'
    l2.touch()
    h1 = d1 / 'h1.bin'
    h1.touch()
    h2 = Path('')

    a1 = d1 / 'active.bin'

    assert (get_segments(d1) == [(l2,h2),(l1,h1)])

def test_segment_iter() -> None:
    d1 = test_dir / 'segment_iter'
    d1.mkdir(exist_ok=True)
    a1 = d1 / 'active.bin'
    a1.touch()
    l1 = d1 / '1.bin'
    l1.touch()
    l2 = d1 / '2.bin'
    l2.touch()
    l3 = d1 / '3.bin'
    l3.touch()
    l17 = d1 / '17.bin'
    l17.touch()
    h1 = d1 / 'h1.bin'
    h1.touch()

    assert(segment_iter(d1, l2) == l1)
    assert(segment_iter(d1, l3) == l2)
    assert(segment_iter(d1, l17) == l3)
    assert(segment_iter(d1, a1) == l17)

# def test_get_hashmap() -> None:
#     d1 = test_dir / 'get_hashmap'
#     d1.mkdir(exist_ok=True)
#     a1 = d1 / 'active.bin'
#     a1.touch()
#     l1 = d1 / '1.bin'
#     l1.touch()
#     h1 = d1 / 'h1.bin'
#     h1.touch()

#     hashmap1 = {"yellow":0}
#     wal.wal_append(wal.package_kv("yellow", "submarine",0),l1)
#     # make hintfile
#     assert(get_hashmap(l1))


def test_tmp_name() -> None:
    d1 = test_dir / 'tmp_name'
    l1 = d1 / '1.bin'
    l2 = d1 / '2.bin'
    l3 = d1 / '3.bin'
    l300 = d1 / '300.bin'
    l301 = d1 / '301.bin'
    t1 = d1 / 't1.bin'
    t2 = d1 / 't2.bin'

    assert tmp_name([l1,l2]) == t1
    assert tmp_name([l2,l300]) == t2


def test_name_funcs() -> None:
    d1 = test_dir / 'hint_name'
    l1 = d1 / '1.bin'
    h1 = d1 / 'h1.bin'
    l300 = d1 / '300.bin'
    h300 = d1 / 'h300.bin'
    t1 = d1 / 't1.bin'

    assert hint_name(l1) == h1
    assert hint_name(l300) == h300
    assert remove_t(t1) == l1

