import ast
import sys
import os

with open(os.path.abspath(sys.argv[-1])) as f:
    fc = f.read()

for i in filter(lambda x: isinstance(x, ast.FunctionDef), ast.parse(fc).body):
    print(i.name)

print("\n\n")

for i in filter(lambda x: isinstance(x, ast.ClassDef), ast.parse(fc).body):
    print(i.name)
    for j in filter(lambda x: isinstance(x, ast.FunctionDef), i.body):
        print("  " + j.name)
