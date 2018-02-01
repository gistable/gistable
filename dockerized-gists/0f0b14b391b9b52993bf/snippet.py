import random

def char_error(s):
	t = ""
	for ch in s:
		if random.randrange(6) == 0:
			t += chr(ord(ch)+random.choice([-1,1]))
		else:
			t += ch
	return t

def combine(s, t):
	u = ""
	for ch1, ch2 in zip(s, t):
		fate = random.randrange(3)
		if fate == 0:
			u += chr((ord(ch1)+ord(ch2))/2)
		elif fate == 1:
			u += ch1
		elif fate == 2:
			u += ch2
	return u

def moire(s, t):
	u = ""
	for ch1, ch2 in zip(s, t):
		if random.randrange(2) == 0:
			u += ch1
		else:
			u += ch2
	return u

def halfsies(s, t):
	return s[:len(s)/2] + t[len(t)/2:]

def sonic_hedgehog(s, t):
	return s[:random.randrange(len(s)/2, len(s))] + t[random.randrange(len(t)/2, len(t)):]

def surface(s, t):
	s_seg_len = random.randrange(len(s)/2)
	s_start = random.randrange(len(s)-s_seg_len)
	t_seg_len = random.randrange(len(t)/2)
	t_start = random.randrange(len(t)-t_seg_len)
	return s[:s_start] + t[t_start:t_start+t_seg_len] + s[s_start+s_seg_len:]

def seg(s):
	seg_len = random.randrange(len(s)/4, len(s)/2)
	start = random.randrange(len(s)-seg_len)
	return s[start:start+seg_len]

def stuck(s):
	t = ""
	tmp = None
	for ch in s:
		if tmp:
			t += tmp
			if random.randrange(2) == 0:
				tmp = None
		else:
			t += ch
			if random.randrange(4) == 0:
				tmp = ch
	return t

def stuck_seg(s):
	return ''.join([seg(s) for i in range(random.randrange(2,6))])

def repeat(s):
	return ''.join([s for i in range(random.randrange(2,5))])

def rot13(s):
	return s.encode('rot_13')

funcs = {
	1: [char_error, char_error, seg, stuck, stuck, stuck_seg, stuck_seg, repeat, rot13],
	2: [combine, moire, halfsies, halfsies, surface, surface, sonic_hedgehog]
}

def glitch(s_list):
	strs = random.sample(s_list, 2)
	if random.randrange(6) == 0:
		strs[0] = random.choice(funcs[1])(strs[0])
	if random.randrange(6) == 0:
		strs[1] = random.choice(funcs[1])(strs[1])
	s = random.choice(funcs[2])(strs[0], strs[1])
	if random.randrange(5) == 0:
		return random.choice(funcs[2])(s, glitch(s_list))
	else:
		return s

if __name__ == '__main__':
	import sys
	strs = sys.argv[1:]
	all_lines = list()
	for line in sys.stdin:
		line = line.strip()
		if len(line) > 0:
			all_lines.append(line)

	for i in range(14):
		print glitch(all_lines)

