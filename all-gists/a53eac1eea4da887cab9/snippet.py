#!/usr/bin/env python

def sec_to_human(secs):
  units = dict({
    7*24*3600: "week",
    24*3600: "day",
    3600: "hour",
    60: "minute",
    1: "second"
  })
  if secs <= 0: return "0 seconds"
  s = list()
  for divisor, name in sorted(units.iteritems(), reverse=True):
    quot=int(secs/divisor)
    if quot:
      if abs(quot) > 1:
        s.append("%s %ss" % (quot, name))
      else:
        s.append("%s %s" % (quot, name))
      secs -= quot * divisor
  return " ".join(s)
