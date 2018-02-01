import json
import requests
import logging as log
log.basicConfig(level=log.DEBUG)


class FollowerExtractor():
    """
    Extracts followers for a given profile
    """

    def __init__(self, username, password):
        self.csrf_token, self.cookie_string = FollowerExtractor.login_instagram(username, password)
        log.info("CSRF Token set to %s", self.csrf_token)
        log.info("Cookie String set to %s" % self.cookie_string)

    @staticmethod
    def get_csrf_and_cookie_string():
        resp = requests.head("https://www.instagram.com")
        return resp.cookies['csrftoken'], resp.headers['set-cookie']

    @staticmethod
    def login_instagram(username, password):
        csrf_token, cookie_string = FollowerExtractor.get_csrf_and_cookie_string()
        data = {"username": username, "password": password}
        resp = requests.post("https://www.instagram.com/accounts/login/ajax/",
                             data=data,
                             headers={
                                 "referer": "https://www.instagram.com/",
                                 "accept": "*/*",
                                 "Accept-Language": "en-GB,en;q=0.8",
                                 "cache-control": "no-cache",
                                 "content-length": "40",
                                 "Content-Type": "application/x-www-form-urlencoded",
                                 "cookie": cookie_string,
                                 "origin": "https://www.instagram.com",
                                 "pragma": "no-cache",
                                 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
                                 "x-csrftoken": csrf_token,
                                 "x-instagram-ajax": "1",
                                 "X-Requested-With": "XMLHttpRequest"
                             })
        return resp.cookies['csrftoken'], resp.headers['set-cookie']

    def extract_followed_by(self, username, user_id=None):
        if user_id is None:
            user_id = json.loads(requests.get("https://www.instagram.com/%s?__a=1" % username).text)['user']['id']

        resp = self.query_followed_by(username, user_id)
        followers = resp['followed_by']['nodes']
        self.save_followed_by(followers)
        while resp['followed_by']['page_info']['has_next_page']:
            resp = self.query_followed_by(username, user_id, resp['followed_by']['page_info']['end_cursor'])
            followers = resp['followed_by']['nodes']
            self.save_followed_by(followers)
            followers += resp['followed_by']['nodes']

        return followers

    def extract_following(self, username, user_id=None):
        if user_id is None:
            user_id = json.loads(requests.get("https://www.instagram.com/%s?__a=1" % username).text)['user']['id']

        resp = self.query_following(username, user_id)
        followers = resp['follows']['nodes']
        self.save_following(followers)
        while resp['follows']['page_info']['has_next_page']:
            resp = self.query_following(username, user_id, resp['follows']['page_info']['end_cursor'])
            followers = resp['follows']['nodes']
            self.save_following(followers)
            followers += resp['follows']['nodes']

        return followers

    def query_following(self, username, user_id, end_cursor=None):
        headers = self.get_headers("https://www.instagram.com/%s" % username)
        post_data = self.get_following_params(user_id, end_cursor)
        req = requests.post("https://www.instagram.com/query/", data=post_data, headers=headers)
        return json.loads(req.text)

    def query_followed_by(self, username, user_id, end_cursor=None):
        headers = self.get_headers("https://www.instagram.com/%s" % username)
        post_data = self.get_followed_by_params(user_id, end_cursor)
        req = requests.post("https://www.instagram.com/query/", data=post_data, headers=headers)
        return json.loads(req.text)

    def get_headers(self, referrer):
        """
        Returns a bunch of headers we need to use when querying Instagram
        :param referrer: The page referrer URL
        :return: A dict of headers
        """
        return {
            "referer": referrer,
            "accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en-GB,en;q=0.8,en-US;q=0.6",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "cookie": self.cookie_string,
            "origin": "https://www.instagram.com",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/49.0.2623.87 Safari/537.36",
            "x-csrftoken": self.csrf_token,
            "x-instagram-ajax": "1",
            "X-Requested-With": "XMLHttpRequest"
        }

    @staticmethod
    def get_followed_by_params(user_id, end_cursor=None):
        """
        Returns the query params required to load next page on Instagram.
        This can be modified to return less information.
        :param tag: Tag we're querying
        :param end_cursor: The end cursor Instagram specifies
        :return: A dict of request parameters
        """
        if end_cursor is None:
            start_query = "ig_user(%s) { followed_by.first(20) {" % user_id
        else:
            start_query = "ig_user(%s) { followed_by.after(%s, 20) {" % (user_id, end_cursor)
        return {
            'q':
                start_query +
                "  count," +
                "  nodes {" +
                "    id," +
                "    is_verified," +
                "    followed_by_viewer," +
                "    requested_by_viewer," +
                "    full_name," +
                "    profile_pic_url," +
                "    username" +
                "  }," +
                "  page_info {" +
                "    end_cursor," +
                "    has_next_page" +
                "  }" +
                "}" +
                " }",
            "ref": "relationships::follow_list"
        }

    @staticmethod
    def get_following_params(user_id, end_cursor=None):
        """
        Returns the query params required to load next page on Instagram.
        This can be modified to return less information.
        :param tag: Tag we're querying
        :param end_cursor: The end cursor Instagram specifies
        :return: A dict of request parameters
        """
        if end_cursor is None:
            start_query = "ig_user(%s) { follows.first(20) {" % user_id
        else:
            start_query = "ig_user(%s) { follows.after(%s, 20) {" % (user_id, end_cursor)
        return {
            'q':
                start_query +
                "  count," +
                "  nodes {" +
                "    id," +
                "    is_verified," +
                "    followed_by_viewer," +
                "    requested_by_viewer," +
                "    full_name," +
                "    profile_pic_url," +
                "    username" +
                "  }," +
                "  page_info {" +
                "    end_cursor," +
                "    has_next_page" +
                "  }" +
                "}" +
                " }",
            "ref": "relationships::follow_list"
        }

    def save_following(self, following):
        """
        Called when a new batch of following users has been extracted from Instagram
        :param following: Users who are following user
        """
        for user in following:
            print("Following: %s" % user['username'])

    def save_followed_by(self, followed_by):
        """
        Called when a new batch of followed_by users has been extracted from Instagram
        :param following: Users who are followed_by
        """
        for user in followed_by:
            print("Followed By: %s" % user['username'])

if __name__ == '__main__':
    instagram_username = "your_username"
    instagram_password = "your_password"
    followed_extractor = FollowerExtractor(instagram_username, instagram_password)
    followed_extractor.extract_following("justintimberlake")
    followed_extractor.extract_followed_by("justintimberlake")
