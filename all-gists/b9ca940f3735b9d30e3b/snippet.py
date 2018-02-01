def _convert_java_millis(java_time_millis):
    """Provided a java timestamp convert it into python date time object"""
    ds = datetime.datetime.fromtimestamp(
        int(str(java_time_millis)[:10])) if java_time_millis else None
    ds = ds.replace(hour=ds.hour,minute=ds.minute,second=ds.second,microsecond=int(str(java_time_millis)[10:]) * 1000)
    return ds


def _convert_datetime_java_millis(st):
    """Provided a python datetime object convert it into java millis"""
    return long(time.mktime(st.timetuple()) * 1e3 + st.microsecond/1e3)
