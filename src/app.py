from multiprocessing import Process
from src.server import serve
from src.my_hash import recreate_hash
from src.segment_manager import compact_and_merge
from pathlib import Path

HOST = ''
PORT = 50007
STORAGE = Path('/usr/key-value/storage/')
STORAGE.mkdir(parents=True, exist_ok=True)
IN_MEMORY_HASH = recreate_hash(STORAGE)
COMPACTION_THRESHOLD = 120

initial_log = STORAGE / "active.bin"
initial_log.touch(exist_ok=True)

serve(HOST, PORT, IN_MEMORY_HASH, STORAGE, COMPACTION_THRESHOLD)

if __name__ == '__main__':
    p = Process(target=compact_and_merge, args=(60.0, STORAGE, 500))
    p.start()
    p.join()

