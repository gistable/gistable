import os
from cStringIO import StringIO
import tarfile
from flask import Flask, Response


app = Flask(__name__)


def get_string_io_len(s):
    pos = s.tell()
    s.seek(0, os.SEEK_END)
    length = s.tell()
    s.seek(pos)
    return length    

class CrazyBuffer(object):
    def __init__(self):
        self._buffer = StringIO()
    def read(self, nbytes=None):
        pass
    def write(self, data):
        self._buffer.write(data)
    def close(self):
        pass
    def tell(self):
        return 0
    def seek(self, offset, whence=None):
        return 0
    def get_value(self):
        return self._buffer.getvalue()
    def reset(self):
        self._buffer.close()
        self._buffer = StringIO()

def streamed_tar_response(files):
    crazy_buffer = CrazyBuffer()
    tar = tarfile.open("test.tar", "w", crazy_buffer)
    for i, f in enumerate(files):
        info = tarfile.TarInfo(name="File_%s.txt" % i)
        #stringIO specific here
        info.size = get_string_io_len(f)
        tar.addfile(info, f)
        yield crazy_buffer.get_value()
        crazy_buffer.reset()
    # Making shit up at this point in case there
    # is someting in the buffer after the loop.
    # Not sure if actually needed!
    tar.close()
    yield crazy_buffer.get_value()

@app.route("/tar", methods=["GET"])
def get_tar():
    files = [
        StringIO("I am file 1."),
        StringIO("I am file 2.")
    ]
    return Response(streamed_tar_response(files), mimetype="application/x-tar")

if __name__ == "__main__":
    app.run()