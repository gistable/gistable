import json
import sys

class ATSFile(object):
	def __init__(self, name):
		self.data = json.load(open(name))
		self.name = name
	def dump(self):
		info = self.data["otherinfo"]
		q = json.loads(info["QUERY"])
		txt = q["queryText"]
		plan = q["queryPlan"]
		open("%s-query.txt" % self.name, "w").write(txt)
		json.dump(plan, open("%s-plan.txt" % self.name,"w"), indent=2)
def main(args):
	data = [ATSFile(f) for f in args]
	for d in data:
		d.dump()

if __name__ == "__main__":
	main(sys.argv[1:])
