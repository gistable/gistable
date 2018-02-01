
class GzipBuffer(object):
    def __init__(self):
        self.len = 0
        self.buffer = io.BytesIO()
        self.writer = gzip.GzipFile(fileobj=self.buffer, mode='wb')

    def append(self, thing):
        self.len += 1
        self.writer.write(thing)

    def flush(self):
        self.writer.close()
        self.buffer.seek(0, 0)
        results = self.buffer.read()
        self.buffer.seek(0, 0)
        self.buffer.truncate()
        self.writer = gzip.GzipFile(fileobj=self.buffer, mode='wb')
        self.len = 0

        return results

    def __len__(self):
        return self.len


buffer = GzipBuffer()
for row in data:
    buffer.append(row)
with open('fakepath', 'wb') as outfile:
    outfile.write(buffer.flush())
