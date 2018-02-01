import urllib2
import json
import urllib
import os
import errno

key = "dl81Vh2uorfNdj2Rt2M4EylW91uUsQRZwhQ99g7K0MRXeMYePS"
baseURL = "http://www.puffchat.me/chatAPI/requestAPI.php"
uploadURL = "http://www.puffchat.me/upload/"


def send_request(argument):
    #Sends a request to PuffChat's shitty API
    url = "%s?%s" % (baseURL, argument)
    try:
        result = urllib2.urlopen(url).read()
    except:
        print "Couldn't load URL: %s" % argument
        raise
    return result


def parse_json(json_string):
    # Parses JSON (kinda says that in the title)
    try:
        json_data = json.loads(json_string)
        formatted_data = format_response(json_data)
    except:
        print "Couldn't decode JSON string: %s" % json_string
        raise

    return formatted_data


def get_user_info(user_name):
    """ Gets user information, this includes:
    birthday, user_name, email & a success flag"""

    print "Getting user: '%s'" % user_name

    arguments = "key=%s&moduleName=getUserInfo&userName=%s" % (key, user_name)
    request = send_request(arguments)
    result = parse_json(request)


    return result


def get_user_friends(user_name, user_email):
    """ Gets user's friends list, this includes:
    emails, ids, status, etc"""

    print "Getting user: '%s' friend list" % user_name

    argument = "key=%s&moduleName=searchFriends&userName=%s&userEmail=%s" % (key, user_name, user_email)
    request = send_request(argument)
    result = parse_json(request)

    return result


def get_user_messages(user_name):
    """ Gets user's received messages """

    print "Getting user: '%s' received messages" % user_name

    argument = "key=%s&moduleName=getMessages&receiverName=%s" % (key, user_name)
    request = send_request(argument)
    result = parse_json(request)

    return result


def get_user_sent_messages(user_name):
    """ Gets user's sent messages """

    print "Getting user: '%s' sent messages" % user_name

    argument = "key=%s&moduleName=getSentMessages&senderName=%s" % (key, user_name)
    request = send_request(argument)
    result = parse_json(request)

    return result


def format_response(response):
    """ Format the JSON response to get rid of shitty status flags etc """

    if response[u'success'] is True:
        return response[u'data']
    elif response[u'success'] is False:
        return False
    else:
        return response


def build_user_file(user_name,):
    """ Builds a json file with user's data, messages, and friends """

    print "Building JSON file for user: %s" % user_name

    # Get user's information
    data = get_user_info(user_name)

    if data is False:
        return False

    user = str(data[u'user_name'])
    email = str(data[u'email'])

    # Get user's Friends
    friends = get_user_friends(user, email)

    formatted_friends = []

    for friend in friends:
        dict = {'friendName': friend[u'friend'], 'friendEmail': friend[u'friend_email'],
                'masterEmail': friend[u'master_email'], 'status': friend[u'status']}

        formatted_friends.append(dict)

    # Get user's messages
    messages = get_user_messages(user)
    sent_messages = get_user_sent_messages(user)
    #get_users_images(messages, user) - This is removed cause it just makes shitty multiples.
    get_users_images(sent_messages, user)

    # Build user data object
    user_data = {user: {'friends': formatted_friends, 'messages': messages, 'sentMessages': sent_messages}}
    file_data = json.dumps(user_data)

    filename = "%s.json" % user
    user_file = open(filename, "w")
    user_file.write(str(file_data))

    return filename


def generate_friend_list(user_name):
    data = get_user_info(user_name)

    if data is False:
        return False

    print "Generating Friend List"
    friends = get_user_friends(data[u'user_name'], data[u'email'])

    unfiltered = []

    for friend in friends:

        if friend[u'status'] == "Cancel":
            continue

        if "@" in friend[u'friend']:  # Crappy API is crappy
            continue

        if "@" in friend[u'master']:  # Crappy API is crappy
            continue

        if " " in friend[u'friend']:  # Crappy API is crappy
            continue

        if " " in friend[u'master']:  # Crappy API is crappy
            continue

        if friend[u'friend'].lower() == user_name.lower():
            unfiltered.append(friend[u'master'])
        elif friend[u'master'].lower() == user_name.lower():
            unfiltered.append(friend[u'friend'])

    return unfiltered


def get_users_images(messages, user_name):
    for message in messages:
        if message[u'filename']:
            path = "Images/%s/" % user_name

            file_path = "%s%s" % (path, message[u'filename'])

            if os.path.isfile(file_path):
                continue

            try:
                os.mkdir(path)
            except OSError as exc:
                if exc.errno == errno.EEXIST and os.path.isdir(path):
                    pass
                else:
                    raise

            print "Downloading image"

            url = "%s%s" % (uploadURL, message[u'filename'])
            try:
                urllib.urlretrieve(url, "Images/%s/%s" % (user_name, message[u'filename']))
            except:
                pass


print "Welcome to PuffGrab, the world's best grabber of the invisible 'secure' puffs from PuffChat."
print "Please note: using this script is completely your responsiblity - don't be a dick."


target_name = raw_input("Enter your target: ")
map_flag = raw_input("Would you like to do this recursively? [Y\N]: ")

if map_flag.lower() == "y":
    friend_list = generate_friend_list(str(target_name))

    filename = build_user_file(target_name)

    if filename:

        print "Done with %s\n" % target_name

        print friend_list

        for friend in friend_list:
            filename = build_user_file(friend)

            print "Done with %s\n" % friend
    else:
        print "User doesn't exist\n"
else:
    filename = build_user_file(target_name)

    if filename:

        print "Done with %s\n" % target_name
    else:
        print "User doesn't exist"

