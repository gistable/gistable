import json
import sys

if __name__ == "__main__":
  data = json.loads(sys.stdin.read())
  print data[sys.argv[1]]
