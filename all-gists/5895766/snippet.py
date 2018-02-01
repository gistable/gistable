class Book:
    ...
    def __hash__(self):
        return hash(self.author) ^ hash(self.other)