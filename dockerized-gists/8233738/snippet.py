#!/usr/bin/env python
import sys, re

hours_re = re.compile(r'([-+] \d+)h \b', re.X)
total = 0

for line in sys.stdin:
	total += sum(int(hour) for hour in hours_re.findall(line))
	print line.strip()

print """
<style>
	.total {
		position: fixed;
		top: 0px;
		right: 10px;
		background-color: #ff6f08;
		color: white !important;
		border-radius: 5px;
		padding: 4px 6px !important;
		line-height: normal;
	}
</style>

<h3 class="total">%s hours</h3>
"""  % (total)
