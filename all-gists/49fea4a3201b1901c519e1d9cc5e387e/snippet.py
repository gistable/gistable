from typing import Tuple, NamedTuple, List, Optional, Dict


class SpendResult(NamedTuple):
    is_successful: bool
    remaining_balance: int


class Bank(object):

    def __init__(self) -> None:
        self.name_to_customer_map: Dict[str, Customer] = {}

    def add_customers(self, *customers: Customer) -> List[bool]:
        results = []
        for customer in customers:
            if customer.name in self.name_to_customer_map:
                results.append(False)
            else:
                self.name_to_customer_map[customer.name] = customer
                results.append(True)
        return results

    def transfer_funds(self, customer_a_name: str, customer_b_name: str, value: int) -> bool:
        if customer_a_name not in self.name_to_customer_map or customer_b_name not in self.name_to_customer_map:
            return False

        primary_acct_a = self.name_to_customer_map[customer_a_name].primary_account
        primary_acct_b = self.name_to_customer_map[customer_b_name].primary_account

        if primary_acct_a is None or primary_acct_b is None:
            return False

        if primary_acct_a.spend(value).is_successful:
            primary_acct_b.credit(value)
            return True
        return False


class Customer(object):

    def __init__(self, name: str) -> None:
        self.name = name
        self.accounts: List[Account] = []
        self.primary_account_name: Optional[str] = None

    def add_account(self, account: Account, is_primary: bool = False):
        self.accounts.append(account)
        if is_primary:
            self.primary_account_name = account.name

    def get_account_by_name(self, name: str) -> Optional[Account]:
        for account in self.accounts:
            if account.name == name:
                return account
        return None

    @property
    def primary_account(self) -> Optional[Account]:
        if self.primary_account_name is None:
            return None
        return self.get_account_by_name(self.primary_account_name)


class Account(object):

    def __init__(self, name: str, initial_balance: int) -> None:
        self.name = name
        self.initial_balance = initial_balance

    def credit(self, value: int) -> bool:
        if value <= 0:
            return False
        self.initial_balance += value
        return True

    def spend(self, value: int) -> SpendResult:
        if value <= 0:
            return SpendResult(False, self.initial_balance)

        if value > self.initial_balance:
            return SpendResult(False, self.initial_balance)

        self.initial_balance -= value
        return SpendResult(True, self.initial_balance)


def sum_two_number(arg_a: int, arg_b: int) -> int:
    return arg_a + arg_b


def main() -> None:
    res = sum_two_number(3, 4)


if __name__ == '__main__':
    main()