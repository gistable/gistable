#! -*- coding: utf-8 -*-


def factor(number):
    """
    Используем разложение на простые множители
    """
    factors = [1]
    start = 2

    while start * start <= n:

        if number % start == 0:
            factors.append(start)
            number //= start
        else:
            start += 1

    if number > 1:
        factors.append(number)

    return factors


if __name__ == '__main__':
    n = int(input('Enter number N: '))
    answers = [factor(number) for number in range(1, n+1)]

    for index, answer in enumerate(answers):
        print(index+1, ' -> ', answer)
