import zipfile
import sys
from pathlib import Path


def unzip(f, encoding, v):
    with zipfile.ZipFile(f) as z:
        for i in z.namelist():
            n = Path(i.encode('cp437').decode(encoding))
            if v:
                print(n)
            if i[-1] == '/':
                if not n.exists():
                    n.mkdir()
            else:
                with n.open('wb') as w:
                    w.write(z.read(i))

if __name__ == '__main__':
    for i in sys.argv[1:]:
        unzip(i, 'cp932', 1)
