import operator

def evaluate(input):
  ops = {'+': operator.add, '-': operator.sub, '*': operator.mul}

	def e(toks, s_num, s_ops):
		if toks == []:
			return s_num.pop()

		try:
			s_num.append(float(toks[0]))
		except ValueError:
			s_ops.append(toks[0])

		if s_ops != [] and len(s_num) >= 2:
			lhs, rhs = s_num.pop(), s_num.pop()
			s_num.append(ops[s_ops.pop()](lhs, rhs))
		return e(toks[1:], s_num, s_ops)

	return e(input.split(), [], [])

def main():
	print evaluate("3 + 1 * 2")

if __name__ == '__main__':
	main()