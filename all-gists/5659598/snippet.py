salt = 65

def incr():
    compiled[pointer] += 1

def decr(): 
    compiled[pointer] -= 1

def fw():
    global pointer
    pointer += 1

def bw():
    global pointer
    pointer -= 1

def print_v():
    result = ''
    for i in compiled:
        result += unichr(i + salt) if i > -1 else '0'
    print('... %s' %result)

functions = {"+": incr, "-": decr, ">": fw, "<":bw, ".": print_v}

while(1):
	compiled = [-1]
	pointer = 0
	code = raw_input('-> ')
	[compiled.append(-1) for char in code if char not in '.[]+-<']
	try:
	    [functions[char]() for char in code]
	except:
	    print("!!! error")