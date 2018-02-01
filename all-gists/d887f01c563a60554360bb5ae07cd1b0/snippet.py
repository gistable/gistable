import time
import hmac
import hashlib
import requests

from urllib.parse import urlencode

PUBLIC_URL = "https://poloniex.com/public"
TRADING_URL = "https://poloniex.com/tradingApi"

class PoloniexAPI:
    def __init__(self, key, secret):
        self.key = key
        self.secret = secret

    def query(self, command, params=None):
        if params is None:
            params = {}

        params["command"] = command
        params["nonce"] = int(time.time() * 1000)

        sign = hmac.new(self.secret.encode("utf-8"), urlencode(params).encode("utf-8"), hashlib.sha512).hexdigest()
        headers = {
            "Sign": sign,
            "Key": self.key
        }
        req = requests.post(TRADING_URL, headers=headers, data=params)
        return req.json()

    # -------------- PUBLIC

    # Returns all currently existing orders for the specified market or all markets
    # Examples: BTC_ETH, BTC_XMR, USD_BTC
    @staticmethod
    def orders(market="all", depth=10):
        params = {"command": "returnOrderBook",
                  "currencyPair": market,
                  "depth": depth}
        req = requests.get(PUBLIC_URL, params=params)
        return req.json()

    # Returns all currently existing loan orders for the specified currency
    # Examples: BTC, ETH, XMR
    @staticmethod
    def loan_orders(currency):
        params = {"command": "returnLoanOrders",
                  "currency": currency}
        req = requests.get(PUBLIC_URL, params=params)
        return req.json()

    # Returns the trading history for the specified market or all markets, start and end must be UNIX timestamps
    # Examples: BTC_ETH, BTC_XMR, USD_BTC
    @staticmethod
    def history(market="all", start=None, end=None):
        params = {"command": "returnTradeHistory",
                  "currencyPair": market,
                  "start": start,
                  "end": end}
        req = requests.get(PUBLIC_URL, params=params)
        return req.json()

    @staticmethod
    def ticker():
        params = {"command": "returnTicker"}
        req = requests.get(PUBLIC_URL, params=params)
        return req.json()

    @staticmethod
    def volume():
        params = {"command": "return24hVolume"}
        req = requests.get(PUBLIC_URL, params=params)
        return req.json()

    # -------------- PRIVATE (requires KEY + SECRET)

    # Returns all !available! balances. Means that provided loans don't count towards your balance.
    def balances(self):
        return self.query("returnBalances")

    # Returns the complete balances of the specified account ( exchange | margin | lending ).
    def account_balances(self, account="lending"):
        params = {"account": account}
        return self.query("returnAvailableAccountBalances", params)

    # Returns all !available! balance, balance on orders and the estimated BTC value of the balance on all accounts.
    def complete_balance(self):
        params = {"account": "all"}
        return self.query("returnCompleteBalances", params)

    # Returns all currently open loan offers
    def open_loan_offers(self):
        return self.query("returnOpenLoanOffers")

    # Returns all currently provided loans
    def active_loans(self):
        return self.query("returnActiveLoans")

    def create_loan_offer(self, currency, amount, rate, duration=2, renew=0):
        params = {
            "currency": currency,
            "amount": amount,
            "duration": duration,
            "lendingRate": rate,
            "autoRenew": renew
        }
        return self.query("createLoanOffer", params)

    def cancel_loan_offer(self, currency, order):
        params = {
            "currency": currency,
            "orderNumber": order
        }
        return self.query("cancelLoanOffer", params)