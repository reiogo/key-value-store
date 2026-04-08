from src.server import serve
from src.my_hash import recreate_hash

HOST = ''
PORT = 50007
STORAGE = '/usr/key-value/storage/tmp.txt'
inMemoryHash = recreate_hash(STORAGE)

serve(HOST, PORT, inMemoryHash, STORAGE)
