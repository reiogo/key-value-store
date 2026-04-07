inMemoryHash = {}

def create() -> dict:
    return inMemoryHash

def get_offset(key:str, h:dict) -> int:
    return h[key]

def update(key:str, offset:int, h:dict) -> bool:
    h[key] = offset
    return h[key] == offset
