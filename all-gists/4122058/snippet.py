from pyparsing import *

stack = {
    "my_number": 4,
    "my_list": []
}

script = \
"""
    push 5 to my_list.
    push 4 to my_list.
    add 4 to my_number.
    remove 5 from my_list.
"""

sentence = Word("push" + "remove" + "add") \
           + Word(nums) \
           + Word("to" + "from") \
           + Word(alphas+"_") \
           + Literal(".")


rule = OneOrMore(Group(sentence))


for action, value, _, destination, _ in rule.parseString(script):

    if action == "push":
        stack[destination].append(value)
    elif action == "remove":
        stack[destination].remove(value)
    elif action == "add":
        stack[destination] += int(value)


print stack # {'my_list': ['4'], 'my_number': 8}