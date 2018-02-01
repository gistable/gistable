# This will cause full debug output to go to the console
>>> import boto
>>> boto.set_stream_logger('foo')
>>> ec2 = boto.connect_ec2(debug=2)
