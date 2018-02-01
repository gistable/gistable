class PringleStack:
    def __init__(self):
        self.stack = []

    def push(self, obj):
        self.stack.append(obj)

    def pop(self):
        while len(self.stack) > 0:
            yield self.stack.pop()
    
stack = PringleStack()

stack.push(1)
stack.push(2)
stack.push(3)

# once you pop, you can't stop
print [item for item in stack.pop()]