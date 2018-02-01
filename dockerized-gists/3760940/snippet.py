import datetime
import requests

BOARD_ID = '505a39b96cd440be5a3ba732'
DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%fz'

# trello api bits - get your own - https://trello.com/1/appKey/generate
API_KEY = '0e62df80c39cd97ef936c405d83b0a23'
API_TOKEN = '45ba8a4f47f4f2290695890464380024ef6852b9fed96dc620dea343bee79ba2'


def yield_latest_comments(board, limit=5, page=0, since='lastView'):
    """ Fetch the latest Trello comments from a board.

        :param board: the id of the board to fetch comments from
        :limit (opt): the number of comments to return - defaults to 5
        :page (opt): the page number (if paging) - defaults to 0 (first page)
        :since (opt): date, Null or lastView (default)

        This uses the `since=lastView` request parameter
        to bring back only the latest comments - but bear
        in mind that this will reset each time the program
        is run, so will need a timestamp check as well.
        Probably.
    """
    url = ('https://trello.com/1/boards/{0}/actions?'
        'filter=commentCard&limit={1}&page={2}&key={3}&token={4}'.format(
            board, limit, page, API_KEY, API_TOKEN))

    data = requests.get(url)
    # TODO: exception handling in case Trello doesn't like our request
    for comment in data.json:
        d = datetime.datetime.strptime(comment['date'], DATE_FORMAT)
        yield (comment['memberCreator']['fullName'],
            comment['data']['card']['name'],
            comment['data']['text'],
            d)

if __name__ == '__main__':

    for sender, card, msg, date in yield_latest_comments(BOARD_ID):
        print 'sender: ' + sender
        print 'card: ' + card
        print 'message: ' + msg
        print 'date: %s' + date
