# 1. Paying the minimum
totalPaid = 0
for month in range(12):
    print("Month: {0:d}".format(month + 1))
    minPayment = balance * monthlyPaymentRate
    totalPaid += minPayment
    print("Minimum monthly payment: {0:.2f}".format(minPayment))
    balance -= minPayment
    balance *= (1 + (annualInterestRate / 12))
    print("Remaining balance: {0:.2f}".format(balance))
print("Total paid: {0:.2f}".format(totalPaid))
print("Remaining balance: {0:.2f}".format(balance))

# 2. Paying debt off in a year
minPayment = 0
newBalance = balance
while newBalance > 0:
    newBalance = balance
    minPayment += 10
    for month in range(12):
        newBalance -= minPayment
        newBalance *= (1 + (annualInterestRate / 12))
print("Lowest payment: {0:d}".format(minPayment))

# 3. Using bisection search
def finalBalance(startBalance, annualInterestRate, monthlyPayment):
    for month in range(12):
        startBalance -= monthlyPayment
        startBalance *= (1 + (annualInterestRate / 12))
    return startBalance

accuracy = 0.000001
lower = balance / 12
upper = (balance * ((1 + (annualInterestRate/12)) ** 12)) / 12
payment = 0.5 * (upper + lower)
finalBal = finalBalance(balance, annualInterestRate, payment)
while abs(finalBal) > accuracy:
    if finalBal< 0:
        upper = payment
    else:
        lower = payment
    payment = 0.5 * (upper + lower)
    finalBal = finalBalance(balance, annualInterestRate, payment)
print("Lowest payment: {0:.2f}".format(payment))