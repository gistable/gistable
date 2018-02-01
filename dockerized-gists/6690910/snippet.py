import sys

def some_name():
    print("function 1")

def some_other_name():
    print("function 2")

if __name__ == "__main__":
    func = getattr(sys.modules[__name__], sys.argv[1])
    func()

# Then run with:
#   python cmd-line-function.py some_name
#   python cmd-line-function.py some_other_name