import time

def guess_time(s):
    """
      >>> guess_time('20:00')
      (20, 0)
      >>> guess_time(' 23:59')
      (23, 59)
      >>> guess_time('20:00foo')
      (20, 0)

      >>> guess_time('9pm')
      (21, 0)
      >>> guess_time('10am')
      (10, 0)
      >>> guess_time('10:30am')
      (10, 30)
      >>> guess_time('10.30am')
      (10, 30)
      >>> guess_time('10:30 pm')
      (22, 30)
      >>> guess_time(' 10AMbar')
      (10, 0)
      >>> guess_time('fubar')
    """
    # See http://docs.python.org/library/time.html#time.strftime
    letters_to_fmts = [
        (8, ['%I:%M %p', '%I.%M %p']),
        (7, ['%I:%M%p', '%I.%M%p']),
        (5, ['%I %p', '%H:%M']),
        (4, ['%I%p']),
        ]

    s = s.lstrip()
    for letters, fmts in letters_to_fmts:
        s1 = s[:letters]
        for fmt in fmts:
            try:
                struct = time.strptime(s1, fmt)
            except ValueError:
                continue
            else:
                return (struct.tm_hour, struct.tm_min)
