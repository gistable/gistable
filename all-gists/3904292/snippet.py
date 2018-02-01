from tempfile import NamedTemporaryFile

def tempfile_path():
    with NamedTemporaryFile(delete=False) as f:
        return f.name

def main():
    print tempfile_path()

if __name__ == '__main__':
    main()