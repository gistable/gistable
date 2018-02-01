def sleep(secs):
  d = Deferred()
  reactor.callLater(secs, d.callback, None)
  return d
