def encode(text):
	if not text:
		return ""
	else:
		last_char = text[0]
		max_index = len(text)
		i = 1
		while i < max_index and last_char == text[i]:
			i += 1
		return last_char + str(i) + encode(text[i:])

print(encode("abbccc"))
# a1b2c3


def decode(text):
	if not text:
		return ""
	else:
		char = text[0]
		quantity = text[1]
		return char * int(quantity) + decode(text[2:])

print(decode("a1b2c3"))
# abbccc