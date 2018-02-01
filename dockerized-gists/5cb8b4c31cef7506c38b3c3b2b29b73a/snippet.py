import numpy as np

def vectorize(x):
    # vectorize a string
    if len(x) > 1:
        return np.sum([vectorize(c) for c in x], axis=0)
    if x == '.':
        i = 27
    elif x == ' ':
        i = 26
    else:
        x = x.lower()
        i = ord(x) - 97
    oh = np.zeros(28)
    oh[i] = 1
    return oh

def decode(x):
    # decode a one hot to a character
    x[-1] += 0.01
    i = np.argmax(x) 
    if i == 27:
        return '.'
    if i == 26:
        return ' '
    return chr(i + 97)

def neural_network(x):
	# matrix mul
	y = np.dot(x, W)
	# softmax
	y = np.exp(y - np.max(y))
	s = np.sum(y)
	y /= s
	return y

def get_reply(message):
	buff = message
	buff_max = 5
	reply = ''
	while(True):
		vec = vectorize(buff)
		nn_out = neural_network(vec)
		c = decode(nn_out)
		reply += c
		if c == '.' or len(reply) > 20:
			break
		buff += c
		buff = buff[-buff_max:]
	return reply


# weights in sparse matrix form
W_sparse = [(3, 4, 2.2), (3, 18, 1.2),
(4, 13, 3.3), (4, 18, 1.7),
(4, 20, 1.2), (4, 26, 0.4),
(4, 27, 2.3), (7, 26, -2.7),
(8, 4, 1.6), (8, 18, 2.4),
(8, 26, 3.6), (8, 27, -1.6),
(13, 3, 2.4), (13, 4, -0.7),
(13, 13, -1.8), (13, 20, 1.9),
(18, 3, 1.8), (18, 4, 2.1),
(18, 13, 2.2), (18, 26, 1.7),
(18, 27, 1.9), (20, 20, -2.1),
(26, 4, 2.9), (26, 13,3.7),
(26, 18, 2.4), (26, 20, 2.2)]

# sparse to dense matrix
W = np.zeros((28, 28))
for r in W_sparse:
	W[r[0], r[1]] = r[2]


print(get_reply('hi'))
