import urllib.request
import json
import decimal

class Bitcoin_cz(object):
    def __init__(self, api_key):
        self.account_data = json.loads(
            urllib.request.urlopen(
                "https://mining.bitcoin.cz/accounts/profile/json/" + api_key
            ).read().decode("utf-8")
        )
        self.block_data = json.loads(
            urllib.request.urlopen(
                "https://mining.bitcoin.cz/stats/json/" + api_key
            ).read().decode("utf-8")
        )

    def print_data(self):
        print()
        print("Username:     " + self.account_data["username"])
        print("Wallet:       " + self.account_data["wallet"])
        print()
        print("Estimated:    \033[0;31m" + self.account_data["estimated_reward"] + "\033[0m BTC")
        print("Unconfirmed:  \033[1;33m" + self.account_data["unconfirmed_reward"] + "\033[0m BTC")
        print("Confirmed:    \033[0;32m" + self.account_data["confirmed_reward"] + "\033[0m BTC")
        print("Total:        " + str(
            decimal.Decimal(self.account_data["unconfirmed_reward"]) + 
            decimal.Decimal(self.account_data["confirmed_reward"])
          ) + " BTC"
        )
        print()
        print(
            "Current round duration: " + 
            self.block_data["round_duration"]
        )
        print("Workers:")
        for worker in self.account_data["workers"]:
            alive = self.account_data["workers"][worker]["alive"]
            print("    " + ("\033[0;31m" if not alive else "\033[0;32m") + worker + "\033[0m")
            print("        Shares: " + str(self.account_data["workers"][worker]["shares"]))
        print()

inst = Bitcoin_cz("insert api key here")
inst.print_data()
