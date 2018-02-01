# Create a quantum, which represents an exact point in time. Internally, the point of time is stored
# as UTC
> t1 = quantum.now()
<Quantum(2014-10-01 20:23:57.745648, no timezone)>

# We can ask for that point of time "at" a certain timezone. Relevant for datemath and display
> t1.at('Pacific/Auckland')
<Quantum(2014-10-01 20:23:57.745648, Pacific/Auckland)>

# We can get a naive datetime out of it at any TZ
> t1.at('UTC').as_local()
datetime.datetime(2014, 10, 1, 20, 23, 57, 745648) 

> t1.at('Pacific/Auckland').as_local()
datetime.datetime(2014, 10, 2, 9, 23, 57, 745648) 

# And format said TZs (there's a strftime of course, format_short is a simple helper)
> t1.at('UTC').format_short()
'1 Oct 2014 20:23'

> t1.at('Pacific/Auckland').format_short()
'2 Oct 2014 09:23'

# Datemath. It cannot be done unless you specify a timezone. If you add "6 months" naively to the UTC
# version, _then_ convert to timezone, chances are your '10am today' is actually '9am' or '11am' in
# six months thanks to a DST change - this is bad, so we disallow it.
> t1.add(months=6)
---------------------------------------------------------------------------
QuantumException                          Traceback (most recent call last)
<ipython-input-9-5513b97edf69> in <module>()
----> 1 t1.add(months=6)

/home/nigel/src/dca/dca2/trex/support/quantum.pyc in add(self, years, months, days, hours, minutes, seconds, microseconds)
    376     def add(self, years=0, months=0, days=0, hours=0, minutes=0, seconds=0, microseconds=0):
    377         if self.tz is None:
--> 378             raise QuantumException("Can't manipulate a Quantum that has no timezone set")
    379         rd = dateutil.relativedelta.relativedelta(years=years, months=months, days=days, hours=hours, minutes=minutes, seconds=seconds, microseconds=microseconds)
    380         local_dt = self.as_local()

QuantumException: Can't manipulate a Quantum that has no timezone set

# Once you specify a tz, it's fine. We just went through a DST transition, so 1 month ago is NOT
# the same hour in UTC:
> t1.at('Pacific/Auckland')
<Quantum(2014-10-01 20:23:57.745648, Pacific/Auckland)>
> t1.at('Pacific/Auckland').subtract(months=1)
<Quantum(2014-09-01 21:23:57.745648, Pacific/Auckland)>

# And when formatted, we can verify that we took 1 month off, through a DST change, and it's still
# the right hour of the day:
> t1.at('Pacific/Auckland').format_short()
'2 Oct 2014 09:23'
> t1.at('Pacific/Auckland').subtract(months=1).format_short()
'2 Sep 2014 09:23'
