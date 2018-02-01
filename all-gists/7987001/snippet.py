import random
choice = random.choice

dha_lo_jd = '━┃┓┛┏┗┳┻┣┫╋'

def generate(num):
	print(''.join([choice(dha_lo_jd) for i in range(num)]))
