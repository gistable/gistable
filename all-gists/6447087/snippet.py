def hotel_cost(nights):
    return nights * 140

bill = hotel_cost(5)

def add_monthly_interest(balance):
    return balance * (1 + (0.15 / 12))

def make_payment(payment, balance):
    owe = balance - payment
    amount = add_monthly_interest(owe)
    #owe =  add_monthly_interest(balance) - payment -(payment * (0.15/12.0))
    print "You still owe: %f" % amount
    return amount

new_bill = make_payment(bill/2, bill)

total = make_payment(100, new_bill)
print total