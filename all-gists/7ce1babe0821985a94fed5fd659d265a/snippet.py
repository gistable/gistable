'''A tool to simplify writing solutions to programming puzzles'''

class Part:

	def __init__(self):
		self.output_buffer = []
		self.accumulator = 0

	def text(self, *text):
		line = ' '.join([str(t) for t in text])
		self.output_buffer.append(line)

	def output(self):
		for line in self.output_buffer:
			print(line)


class Puzzle(dict):
	
	def new_part(self, name):
		self[name] = Part()

	def output(self):
		for name, part in self.items():
			print('\n' + str(name) + ':')
			part.output()

	# Allow 'with Puzzle as p'
	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		self.output()

if __name__ == '__main__':
  import random
  with Puzzle() as p:
    for name in ['Power {}'.format(y) for y in range(5)]:
      p.new_part(name)
    for part in p.values():
      part.accumulator = sum([random.randint(0, 1000) for _ in range(50)])
      part.text('placeholder:', part.accumulator)