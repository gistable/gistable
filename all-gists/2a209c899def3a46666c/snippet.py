array = []
for i in range(5):
    def demo():
        return i
    array.append(demo)

[item() for item in array]
