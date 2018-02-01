from __future__ import division

import collections
from texttable import Texttable

by_status = collections.defaultdict(list)
per_page = 100
offset = 0

while True:
    stripe_customers = stripe.Customer.all(count=per_page, offset=offset)

    if not stripe_customers['data']:
        break

    for c in stripe_customers['data']:
        if c.subscription:
            by_status[c.subscription.status].append(c)
        else:
            by_status['none'].append(c)

    offset += per_page


total_monthly_revenue = []

for type, customers in by_status.iteritems():

    print '*' * 80
    print 'Subscriptions: ', type, ' - ', len(customers)
    print '*' * 80
    table = Texttable()
    table.set_deco(Texttable.HEADER)
    table.set_cols_align(['l', 'r', 'l', 'r'])
    table.header(['Customer', 'Plan', 'Coupon', 'Monthly'])
    table.set_precision(2)

    for c in customers:
        row = []
        row.append(c.description or c.email)

        monthly = 0
        if c.subscription:
            amount = '$%d' % (c.subscription.quantity * c.subscription.plan.amount / 100)
            if c.subscription.plan.interval == 'month':
                monthly = c.subscription.quantity * c.subscription.plan.amount
            elif c.subscription.plan.interval == 'year':
                amount += ' ANNUAL'
            else:
                amount += ' %s!!!' % c.subscription.plan.interval
        else:
            amount = '-'
        row.append(amount)


        coupon = '-'
        if c.discount:
            if c.discount.coupon.duration == 'forever':
                if c.discount.coupon.percent_off:
                    coupon = monthly * (c.discount.coupon.percent_off / 100)
                    monthly -= coupon
                    coupon = '%d%%' % c.discount.coupon.percent_off
                elif c.discount.coupon.amount_off:
                    coupon = c.discount.coupon.amount_off
                    monthly -= coupon
                    coupon = '$%d' % (coupon / 100)
                else:
                    print c.discount
            else:
                print c.discount
        row.append(coupon)

        row.append('$%d' % (monthly / 100))

        # exclude 'canceled' customers who no longer have a subscription
        # but include past_due, unpaid, and trialing because we still expect
        # to get this money
        if c.subscription:
            total_monthly_revenue.append(monthly)

        table.add_row(row)

    print table.draw() + "\n\n"

print '=' * 30
print 'TOTAL MONTHLY REVENUE'
print '=' * 30
print '$%d' % (sum(total_monthly_revenue) / 100)
print '=' * 30
