#!/usr/bin/python

import ledger
import sys
import re

def account_name(post):
    account = post.account.fullname().replace(" ","").replace("(","").replace(")","").replace("'","")
    return re.sub(r'\:(\d)',r':X\1', account)
    

def get_symbol(amount):
  symbol = amount.commodity.symbol.replace("-","").replace("\"","").upper()
  if symbol == "$":
    symbol = "USD"
  return symbol


filename = sys.argv[1]
accounts = set()
for xact in ledger.read_journal(filename).xacts():
  for post in xact.posts():
    account = account_name(post)
    if account not in accounts:
          print "%s open %s" % (xact.date, account)
          accounts.add(account)
  print "%s * \"%s\"" % (xact.date, xact.payee)
  for post in xact.posts():
    account = account_name(post)
    symbol = get_symbol(post.amount)
    if post.amount.has_annotation():
        price = post.amount.price()
        if post.amount.number() != 0:
            price = price / post.amount.number()
        psym = get_symbol(price)
        print "  %-50s  %s %s @ %s %s" % (account, post.amount.number(), symbol, price.number(), psym)
    else:
        print "  %-50s  %s %s" % (account, post.amount.number(), symbol)



