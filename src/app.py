from multiprocessing import Process
from src.server import serve
from src.my_hash import recreate_hash
from src.disk_manage import compact_and_merge
from pathlib import Path

HOST = ''
PORT = 50007
STORAGE = Path('/usr/key-value/storage/')
initial_log = STORAGE / "active.bin"
if not initial_log.exists():
    initial_log.touch()
inMemoryHash = recreate_hash(STORAGE)

serve(HOST, PORT, inMemoryHash, STORAGE)

if __name__ == '__main__':
    p = Process(target=compact_and_merge, args=(60.0, STORAGE, 500))
    p.start()
    p.join()

