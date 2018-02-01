import math

def total_cost(amount):
    return int(math.ceil(amount + 0.5 + 0.01 * amount))

def reduce_balance(balance, amount):
    if amount < balance:
        balance -= total_cost(amount)
    return balance

def checkio(data):
    balance, amounts = data
    
    amounts = filter(lambda x: x % 5 == 0 and x > 0, amounts)
    
    return reduce(reduce_balance, amounts, balance)
    
if __name__ == '__main__':
    assert checkio([120, [10 , 20, 30]]) == 57, 'First'

    # With one Insufficient Funds, and then withdraw 10 $
    assert checkio([120, [200 , 10]]) == 109, 'Second'

    #with one incorrect amount
    assert checkio([120, [3, 10]]) == 109, 'Third'

    assert checkio([120, [200, 119]]) == 120 , 'Fourth'

    assert checkio([120, [120, 10, 122, 2, 10, 10, 30, 1]]) == 56, "It's mixed all base tests"
    
    print('All Ok')