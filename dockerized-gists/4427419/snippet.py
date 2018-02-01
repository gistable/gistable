# -*- coding: utf-8 -*-

def fibonacci_word(n) :
    if n < 0 :
        return None
    elif n == 0 :
        return [1]
    elif n == 1 :
        return [0]
    else :
        f_n_1 = fibonacci_word(n - 1)
        f_n_2 = fibonacci_word(n - 2)
        return f_n_1 + f_n_2

def draw_fibonacci_word(fib_word, step = 10) :
    import turtle
    turtle.setworldcoordinates(0, 0, 800, 600)
    turtle.Screen()
    turtle.home()

    for i, symbol in enumerate(fib_word) :
        turtle.forward(step)
        if symbol == 0 and i % 2 == 0 :
            turtle.left(90)
        elif symbol == 0 and i % 2 == 1 :
            turtle.right(90)

    raw_input("Press Enter to continue...")
    turtle.bye()

def main() :
    n = int(raw_input("Enter an integer for n:"))
    fib_word_n = fibonacci_word(n)
    draw_fibonacci_word(fib_word_n)

if __name__ == '__main__':
    main()
