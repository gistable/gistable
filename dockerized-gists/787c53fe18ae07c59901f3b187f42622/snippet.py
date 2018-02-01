def calculate_tax(names):
    try:
        new_dict = {}
        for name in names:
            a = [0, 1000, 10000, 20200, 30750, 50000]
            b = [1000, 10000, 20200, 30750, 50000, 100000]
            p = [0, .1, .15, .2, .25, .3]
            amount = names[name]
            tax = 0
            i = 0
            while amount > 0:
                rate = b[i] - a[i]
                if (amount < rate and i != 5):
                    tax += (amount * p[i])
                    amount = 0
                    i += 1
                elif i != 5:
                    tax += (rate * p[i])
                    amount -= rate
                    i += 1
                else:
                    # Last elem
                    if (amount < rate):
                        tax += (amount * p[i])
                        amount = 0
                    else:
                        tax += (0.3 * 50000)
                        amount -= rate
                        i = 5

            new_dict[name] = tax
        return new_dict

    except (AttributeError,TypeError):
        raise ValueError('The provided input is not a dictionary')

print(calculate_tax({
    'Alex': 500,
    'James': 20500,
    'Kinuthia': 70000
}))