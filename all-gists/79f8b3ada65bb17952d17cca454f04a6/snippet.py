if __name__ == "__main__":
    base_url = "https://api.pinnaclesports.com"
    username = <username>
    password = <password>

    stake = 1.5

    balance = get_balance(base_url, username, password)
    odds = get_sport_odds(base_url, username, password)
    bet = find_bet(odds)

    if len(bet) > 0:
        get_bet_info(base_url, username, password, bet)
    else:
        print("No bets matching criteria")

    if stake >= bet['minRiskStake'] and stake < balance['availableBalance']:
        place_bet(base_url, username, password, bet, stake)
    else:
        print("Stake too small, or not enough funds")