"""
Simple python script to upload a file to Trello.

This script is a demo - done to show how to do it - it doesn't have
much practical purpose as it requires the use of a number of tokens
and identifiers which you can only get programmatically or by visiting
the website (in which case you may as well upload the attachment directly.)

You should read the Trello API docs prior to using this:
    https://trello.com/docs/gettingstarted/index.html

You will need the following in order to use this:

1. A Trello API application key. You can get this from
    https://trello.com/docs/gettingstarted/index.html

2. A user token that has write access. You can get one of these (for yourself)
    by logging in to Trello and going to https://trello.com/1/authorize?key=substitutewithyourapplicationkey&name=My+Application&expiration=1day&response_type=token&scope=read,write
    (obviously substituting your key from step one above into the url)

3. The id of the card to upload to. This is harder to find as a human being -
    it's returned via the API, but doesn't appear in the address bar anywhere.
    However, you can use the card 'short link' instead :-). To find this, open
    the card in the website, click on the 'More' link in the bottom right of
    the card, then copy the id from the card link. e.g. if the link is
    https://trello.com/c/E3XMd91s then use E3XMd91s as the id.

"""
import argparse
import requests

ATTACHMENTS_URL = 'https://api.trello.com/1/cards/%s/attachments'


def upload_file_to_trello_card(key, token, card_id, file_path):
    """
    Upload a local file to a Trello card as an attachment.

    File must be less than 10MB (Trello API limit).

    :param key: Trello API app key
    :param token: Trello user access token - must have write access
    :param card_id: The relevant card id
    :param file_path: path to the file to upload

    Returns a request Response object. It's up to you to check the
        status code.
    """
    params = {'key': key, 'token': token}
    files = {'file': open(file_path, 'rb')}
    url = ATTACHMENTS_URL % card_id
    return requests.post(url, params=params, files=files)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--token',
        help='Trello API user access token', required=True)
    parser.add_argument('-k', '--key',
        help='Trello API app key', required=True)
    parser.add_argument('-c', '--card',
        help='Trello card identifier', required=True)
    parser.add_argument('-f', '--file',
        help='Path to file to be uploaded', required=True)
    args = parser.parse_args()

    resp = upload_file_to_trello_card(
        args.key, args.token, args.card, args.file
    )
    print "%s\n%s" % (resp, resp.text)
