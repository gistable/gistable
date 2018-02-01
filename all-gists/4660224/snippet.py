def normalize_line(line):
    return [piece.strip() for piece in line.split("|")[1:-1]]

def is_valid_line(line):
    return "|" in line

def load(text):
    lines =  map(normalize_line,
                filter(is_valid_line,
                        text.strip().splitlines()))
    keys = lines.pop(0)
    return [dict(zip(keys, line)) for line in lines]


print load("""
 -------------------------------------------
 | username | password | email             |
 -------------------------------------------
 | edi      | 123456   |                   |
 | budu     | 123456   | edi@edi.com       |
 | budu     | 123456   | budu@budu.com     |
 | budu     | 123456   | budu@budu.com     |
 | budu     | 123456   | budu@budu.com     |
 -------------------------------------------
""")