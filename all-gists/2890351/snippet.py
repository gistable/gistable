In [1]: import boto

In [2]: c = boto.connect_s3()

In [3]: b = c.lookup('stats.pythonboto.org')

In [4]: k = b.new_key('test1234')

In [5]: def mycb(so_far, total):
   ...:     print '%d bytes transferred out of %d' % (so_far, total)
   ...: 

In [6]: k.set_contents_from_filename('detail.html', cb=mycb, num_cb=10)
0 bytes transferred out of 19837
8192 bytes transferred out of 19837
16384 bytes transferred out of 19837
19837 bytes transferred out of 19837
