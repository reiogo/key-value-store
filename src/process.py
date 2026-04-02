import re
import os
def parser(raw_data):
    data = raw_data.decode("utf-8")

    pat = re.compile(r"(GET|PUT)?\s?([a-zA-Z0-9]*)?\s?([a-zA-Z0-9]*)?")
    m = pat.search(data)

    if m:
        action = m.group(1)
        key = m.group(2)
        value = m.group(3)
        return (action, key, value)
    else:
        return ("NULL", "", "")

def process(action, key, value):
    pass

