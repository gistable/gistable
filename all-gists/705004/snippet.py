#!/usr/bin/python
import csv
import json
import hashlib
import random
import string
from optparse import OptionParser

def random_string(length):
    char_set = string.ascii_letters + string.digits
    return ''.join(random.sample(char_set,length))

def get_django_password(password):
    salt = random_string(5) 

    hashed = hashlib.sha1(salt + password).hexdigest()

    return "sha1$%s$%s" % (salt, hashed)


def get_user_object(user, key):
    return {
        "model": "auth.user",
        "pk": key,
        "fields": {
            "username": user["username"],
            "first_name": "",
            "last_name": "",
            "is_active": True,
            "is_superuser": False,
            "is_staff": True,
            "last_login": "2010-10-10 14:11:49",
            "groups": [],
            "user_permissions": [],
            "password": get_django_password(user["password"]),
            "email": "",
            "date_joined": "2010-10-10 14:11:49"
        }
    }


def create_fixture(csv_file, dry_run=False, option_filename=None):
    
    if option_filename:
        custom_options = json.load(open(option_filename, 'r'))
    else:
        custom_options = {}
    
    options = {
        "delimiter": (str(custom_options["delimiter"]) if
                        custom_options.has_key("delimiter") else ","),
    }
    users = csv.DictReader(open(csv_file, 'r'), delimiter=options["delimiter"])
    if dry_run:
        user = users.next()
        return json.dumps(get_user_object(user,1))

    else:
        output_list = []
        for index, user in enumerate(users):
            if user["username"] != "":
                output_list.append(get_user_object(user, index+1))

        return json.dumps(output_list)


if __name__ == "__main__":
    usage = "usage: %prog [options] CSV_FILE"
    parser = OptionParser(usage=usage)
    parser.add_option("-d", "--dry-run", action="store_true", 
                      dest="dry_run", default=False, 
                      help="Only show an example, to see if the CSV is properly formed")
    parser.add_option("-o", "--option_file", action="store",
                      dest="option_file",
                      help="Provide a JSON valid file with an option object. Right now, only \"delimiter\" option is supported.",
                      metavar="OPTION_FILE")
    (options, args) = parser.parse_args()
    print create_fixture(args[0], options.dry_run, options.option_file)