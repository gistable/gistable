# brew install rtmpdump
print ' && '.join(['rtmpdump -r "rtmp://streamcloud.klewel.com/cfx/st/v0/djangocon-2012-flash-%d.flv" -o djangocon-2012-flash-%d.flv' % (i, i) for i in xrange(1, 45 + 1)])