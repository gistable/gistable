# SCREW YOU CONDITIONALS
def fizzbuzz(n):
    fizzes = [1, 0, 0]
    buzzes = [2, 0, 0, 0, 0]
    words = [None, "Fizz", "Buzz", "FizzBuzz"]

    for i in range(1, n):
        words[0] = i
        print(words[fizzes[i%3] + buzzes[i%5]])

fizzbuzz(20)
