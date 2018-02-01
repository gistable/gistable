from decimal import Decimal
from datetime import timedelta


def duration(duration_string): #example: '5d3h2m1s'
	duration_string = duration_string.lower()
	total_seconds = Decimal('0')
	prev_num = []
	for character in duration_string:
		if character.isalpha():
			if prev_num:
				num = Decimal(''.join(prev_num))
				if character == 'd':
					total_seconds += num * 60 * 60 * 24
				elif character == 'h':
					total_seconds += num * 60 * 60
				elif character == 'm':
					total_seconds += num * 60
				elif character == 's':
					total_seconds += num
				prev_num = []
		elif character.isnumeric() or character == '.':
			prev_num.append(character)
	return timedelta(seconds=float(total_seconds))