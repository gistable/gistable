"""
A simple example of calling commands with a dict instead of an if/elif/else
chain.
"""
import sys  # used for argv, not really imprtant for the example

def main():
    # Create a dictionary of commands and their corresponding function
    # This function can be called by using the command as a keyword when
    # accessing the dictionary.
    # my_commands["add"](1, 3) returns 4
    my_commands = {
        "add": add,
        "subtract": sub,
        "sub": sub,
        "multiply": mul,
        "mul": mul,
        "divide": div,
        "div": div
    }

    # Use sys.argv to easily demo this concept
    if sys.argv[1] in my_commands:
        try:
            cmd = sys.argv[1]
            a = int(sys.argv[2])
            b = int(sys.argv[3])
            print(cmd,a,b)
            print(my_commands[cmd](a,b))
        except:
            print("Please pass an arithmetic operator and two numbers")
            print("EXAMPLE: $ python command.py add 1 2")

"""
Define your basic arithmetic functions, each taking two arguments.
"""
def add(a, b):
    return a+b

def sub(a, b):
    return a-b

def mul(a, b):
    return a*b

def div(a, b):
    return a/b

if __name__ == "__main__":
    main()