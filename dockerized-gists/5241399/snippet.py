def file_is_binary(filename):
    with open(filename) as fp:
        return chr(0) in iter(fp.read(8000))