# bad case
try:
    do_something() 
    log.debug(u"complete")  # if error raise here, code can't detect error.
except:
    log.debug(u"error") 

# good case
try:
    do_something()
except:
    log.debug(u"error")
else:
    log.debug(u"complete")