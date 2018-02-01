# by sgk

import datetime

class TZ(datetime.tzinfo):
  def __init__(self, name, offset):
    self.name_ = name
    self.offset_ = offset
  def utcoffset(self, dt):
    return datetime.timedelta(hours=self.offset_)
  def tzname(self, dt):
    return self.name
  def dst(self, dt):
    return datetime.timedelta(0)

UTC = TZ('UTC', 0)
JST = TZ('JST', 9)

def jst_from_utc(dt):
  return dt.replace(tzinfo=UTC).astimezone(JST)

def utc_from_jst(dt):
  return dt.replace(tzinfo=JST).astimezone(UTC)

def as_jst(dt):
  return dt.astimezone(JST)

def as_utc(dt):
  return dt.astimezone(UTC)
