import requests
import sys
import random
import csv

from time import sleep

rand = random.Random()


def check_account(username, password):
    """
    Checks if a given account is valid.

    :param username: The username
    :param password: The password
    :return: a tuple, the first value being True or False regarding on if the account still exists, and the second an
    object: if valid, it contains None; else, four keys ('http_code', 'error', 'message', 'cause').
    """
    r = requests.post('https://authserver.mojang.com/authenticate', json={
        'agent': {
            'name': 'Minecraft',
            'version': 1
        },
        'username': username,
        'password': password,
        'clientToken': rand.getrandbits(256)
    })

    if r.ok:
        return True, None

    else:
        json_error = r.json()

        data = {
            'http_code': r.status_code,
            'error': json_error['error'],
            'message': json_error['errorMessage'],
            'cause': json_error['cause'] if 'cause' in json_error.keys() else None
        }
        return False, data


def is_file_empty(filename):
    """
    Checks if a file is empty.

    :param filename: The filename.
    :return: True if the file does not exists or is empty.
    """
    try:
        with open(filename) as f:
            for file_line in f:
                if file_line:
                    return False

        return True
    except FileNotFoundError:
        return True


def save(filename, username, password, error=None):
    """
    Writes a dict to a CSV file. The content is appended if the file is not empty.
    :param filename: The CSV file name.
    :param username: The username.
    :param password: The password.
    :param error: The error encountered, as returned by the check_account method: keys 'http_code', 'error', 'message',
    'cause'.
    """
    print_headers = is_file_empty(filename)

    if not error:
        error = {
            'error': '',
            'message': '',
            'cause': '',
            'http_code': 200
        }

    with open(filename, 'ab') as f:
        if print_headers:
            f.write(bytes('username\tpassword\terror\terror_message\terror_cause\terror_http_code\r\n', 'UTF-8'))

        data = username + '\t' + password + '\t'
        data += str(error['error']) + '\t' + str(error['message']) + '\t' + str(error['cause']) + '\t'
        data += str(error['http_code'])
        data += '\r\n'

        f.write(bytes(data, 'UTF-8'))


def load(filename: str, import_to: list):
    """
    Stores the usernames in the given CSV file (under the column 'username') in the import_to list.
    :param filename: The CSV file (dialect: excel-tab).
    :param import_to: The list where the usernames will be stored
    """
    try:
        with open(filename, 'r') as f:
            reader = csv.DictReader(f, dialect='excel-tab')
            for row in reader:
                import_to.append(row['username'])
    except FileNotFoundError:
        pass


# ----------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    if len(sys.argv) <= 1:
        sys.stderr.write('Usage: ' + sys.argv[0] + ' <path to the file with users names and passwords>\n')
        sys.stderr.write('The file containing the credentials must be formatted with a couple username/password '
                         'per line, separated by a colon\n')
        sys.exit(1)

    valid_accounts_file = 'valid_accounts.csv'
    invalid_accounts_file = 'invalid_accounts.csv'

    max_tries_per_account = 5
    waiting_seconds_on_rate_limit = 45
    waiting_seconds_between_requests = 2

    accounts = []
    already_imported_accounts = []

    valid_accounts = []
    invalid_accounts = []

    try:
        with open(sys.argv[1]) as f:
            for line in f:
                user_pass = line.strip().split(':', maxsplit=1)
                if len(user_pass) is not 2:
                    sys.stderr.write('Invalid credential format in file: "{0}", skipping\n'.format(line.strip()))
                    continue

                accounts.append({'user': user_pass[0], 'pass': user_pass[1]})

    except FileNotFoundError:
        sys.stderr.write('Unable to open the input file ' + sys.argv[1] + '\n')
        sys.exit(1)

    if not accounts:
        sys.stderr.write('No account found in the given file\n')
        sys.exit(0)

    print('Checking {0} accounts'.format(len(accounts)))
    print('Data saved to {0} and {1}.'.format(valid_accounts_file, invalid_accounts_file))

    load(valid_accounts_file, already_imported_accounts)
    load(invalid_accounts_file, already_imported_accounts)

    print('{0} accounts already imported'.format(len(already_imported_accounts)))

    print()

    for account in accounts:
        if account['user'] in already_imported_accounts:
            print('Account {0} already checked, skipping.'.format(account['user']))
            continue

        for _ in range(max_tries_per_account):
            print('Checking account {0}... '.format(account['user']), end='')
            valid, error = check_account(account['user'], account['pass'])

            if valid:
                print('VALID')
                valid_accounts.append(account)
                save(valid_accounts_file, username=account['user'], password=account['pass'])
                break
            else:
                if error['message'].strip() == 'Invalid credentials.':
                    print('Rate-limited. Waiting {0} seconds.'.format(waiting_seconds_on_rate_limit))
                    sleep(waiting_seconds_on_rate_limit)
                    continue

                print('INVALID: HTTP {0}: "{1}"'.format(error['http_code'], error['message']))
                save(invalid_accounts_file, username=account['user'], password=account['pass'], error=error)
                break

        sleep(waiting_seconds_between_requests)

    print('Done. {0} accounts still valid, and {0} invalid.'.format(len(valid_accounts), len(invalid_accounts)))
