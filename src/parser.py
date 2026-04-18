import re
def parser(raw_data:bytes) -> tuple[str, str, str]:
    data = raw_data.decode("utf-8")

    pat = re.compile(r"(DELETE|GET|PUT)\s*([^\s]*)?\s*([^\s]*)?")
    m = pat.search(data)

    if m:
        action = m.group(1)
        key = m.group(2)
        value = m.group(3)
        return (action, key, value)
    else:
        return ("NULL", "", "")
