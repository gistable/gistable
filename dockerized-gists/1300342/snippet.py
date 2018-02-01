from subprocess import Popen, PIPE
import re
import glob
import shlex

class Pipeline(object):
	def __init__(self, descriptor=None):
		self.steps = []
		if descriptor:
			for step in descriptor.split("|"):
				self.add(step.strip())

	def __repr__(self):
		return " | ".join(self.steps)

	def add(self, step, pos=None):
		if pos:
			self.steps.insert(pos, step)
		else:
			self.steps.append(step)
			pos = len(self.steps) - 1
		return pos

	# syntactic sugar
	def __or__(self, step):
		self.add(step)
		return self

	def remove(self, pos):
		del self.steps[pos]

	def run(self):
		procs = {}
		procs[0] = Popen(shlex.split(self.steps[0]), stdout=PIPE)
		if len(self.steps) > 1:
			i = 1
			for p in self.steps[1:]:
				procs[i] = Popen(shlex.split(p), stdin=procs[i-1].stdout, stdout=PIPE)
				procs[i-1].stdout.close()
		output = procs[len(procs) - 1].communicate()[0]
		return output

class PipelineWithSubstitutions(Pipeline):
	def __init__(self, descriptor=None, substitutions=None):
		Pipeline.__init__(self, descriptor)
		self.substitutions = substitutions

	def add(self, step, pos=None):
		for sub in self.substitutions:
			step = re.sub(sub, self.substitutions[sub], step)
		Pipeline.add(self, step, pos)

if __name__ == "__main__":
	import os.path

	p = Pipeline() | "ls"
	print p.run()	
	
	p = Pipeline() | "ls -s" | "sort -n"
	print p.run()

	a = ["bib.bib", "test.bib"]
	a = []
	p = PipelineWithSubstitutions(
			substitutions={
				"%%": "CURRENT_FILE",
				"%:r": os.path.splitext("CURRENT_FILE_N")[0],
				"PANDOC#BIBS" : " ".join(["--bibliography " + i for i in a])
				}
#			) | "pandoc -t json %%" | "filter" | "pandoc PANDOC#BIBS -f json -t -o latex %:r.latex"
			) | "pandoc PANDOC#BIBS -t html -Ss -o %:r.html %%"
	print p
