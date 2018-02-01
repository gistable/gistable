"""Adder 0.2 - Snake based language...for adding"""


class Snake:
    """The main body of the adder"""
    skin = '>'

    def __init__(self):
        self.body = ''

    def add(self):
        self.body += self.skin

    def __str__(self):
        return unicode(self.body).encode('utf-8')


def main():
    snake = Snake()

    while (1):
        command = raw_input()
        if command == 'add':
            snake.add()
            print snake

if __name__ == "__main__":
    main()
