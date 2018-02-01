import json
from os.path import exists
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException


class GoogleGroupsScraper(object):
    """ A simple class to scrape a google group. """

    #### object interface #####################################################

    def __init__(self, url, verbose=False, persistence_file='group.json'):
        self.url = url
        self.driver = self._get_driver()
        self.wait = WebDriverWait(self.driver, 30)
        self.verbose = verbose

        self.persistence_file = persistence_file
        self.thread_urls = []
        self.raw_urls = []
        self._current_thread_index = -1
        self._current_message_index = -1
        self._get_state()

    #### GoogleGroupsScraper interface ########################################

    def get_all_thread_urls(self):
        """ Return and persist the urls for all the threads. """

        if len(self.thread_urls) == 0:
            self.driver.get(self.url)
            post_list = self._scroll_to_get_all_posts()
            self.thread_urls = self._get_urls_from_post_list(post_list)

        else:
            print 'Using persisted urls ...'

        if self.verbose:
            print 'Found %d threads.' % len(self.thread_urls)

        self._set_state()

    def get_all_raw_urls(self):
        """ Return all the raw urls in the forum. """

        self.get_all_thread_urls()

        for i, url in enumerate(self.thread_urls):
            if i <= self._current_thread_index:
                continue
            if self.verbose:
                print 'Fetching raw urls in thread: %d' % i
            self.raw_urls.extend(self._get_all_raw_urls_in_thread(url))
            self._current_thread_index = i
            self._set_state()

        return self.raw_urls

    def save_all_posts(self):
        """ Save all the posts to a persist directory. """

        self.get_all_raw_urls()

        for i, url in enumerate(self.raw_urls):
            if i <= self._current_message_index:
                continue
            if self.verbose:
                print 'Saving message %d of %d' % (i, len(self.raw_urls))
            self._save_content_of_messages(url)
            self._current_message_index = i
            self._set_state()

    #### Private interface ####################################################

    def _get_driver(self):
        """ Get the web-driver for the scraper. """

        driver = webdriver.Firefox()
        driver.implicitly_wait(30)

        return driver

    def _get_all_raw_urls_in_thread(self, thread_url):
        """ Return the raw urls of all the messages in the given thread. """

        self.driver.get(thread_url)

        # fixme: see if javascript finished loading...
        try:
            WebDriverWait(self.driver, 3).until(lambda d: False)
        except TimeoutException:
            pass

        message_ids = self._get_all_message_ids()

        raw_urls = [
            self._get_raw_url(thread_url, message_id)
            for message_id in message_ids
        ]

        if self.verbose:
            print 'Obtained %s raw urls.' % len(raw_urls)

        return raw_urls

    def _get_all_message_buttons(self):
        """ Return all the message buttons on the page. """

        timeline = self.driver.find_element_by_id('tm-tl')
        all_buttons = timeline.find_elements_by_class_name(
            'jfk-button-standard'
        )

        return all_buttons

    def _get_all_message_ids(self):
        """ Return all the message ids given a timeline with list of messages.

        """

        all_buttons = self._get_all_message_buttons()
        message_buttons = [
            el for el in all_buttons
            if el.get_attribute('aria-label').startswith('More')
        ]
        message_ids = [
            button.get_attribute('id')[len('b_action_'):]
            for button in message_buttons
        ]

        return message_ids

    def _get_last_post(self):
        """ Get the currently displayed last post. """

        post_list = self._get_post_list()
        last_post = post_list.find_elements_by_class_name('GIURNSTDIQ')[-1]
        # Hack to scroll to the last post
        last_post.location_once_scrolled_into_view

        return last_post

    def _get_state(self):
        """ Return the persisted urls of a post, from a previous run. """

        if exists(self.persistence_file):
            with open(self.persistence_file) as f:
                data = json.load(f)
                for attr in ['raw_urls', 'thread_urls']:
                    setattr(self, attr, data.get(attr, []))

                self._current_thread_index = data.get(
                    'current_thread_index', -1
                )

                self._current_message_index = data.get(
                    'current_message_index', -1
                )

    def _set_state(self):
        """ Save the state to the persistence file. """
        # fixme: persist everything to separate files!
        data = {
            'current_thread_index': self._current_thread_index,
            'current_message_index': self._current_message_index,
            'thread_urls': self.thread_urls,
            'raw_urls': self.raw_urls,
        }

        with open(self.persistence_file, 'w') as f:
            if self.verbose:
                print 'Saving state ...'
            json.dump(data, f, indent=2)

    def _get_post_list(self):
        """ Get the list of posts currently visible in a groups page. """

        return self.driver.find_element_by_class_name('GIURNSTDGBC')

    def _get_raw_url(self, thread_url, message_id):
        """ Return the raw url given the thread_url and the message_id. """

        _, group, thread_id = thread_url.rsplit('/', 2)
        url_fmt = 'https://groups.google.com/forum/message/raw?msg=%s/%s/%s'

        return url_fmt % (group, thread_id, message_id)

    def _get_urls_from_post_list(self, post_list):
        """ Given a post_list element, return the urls of all the posts. """

        print 'Fetching post urls from all the displayed posts ...'
        urls = [
            el.get_attribute('href')
            for el in post_list.find_elements_by_tag_name('a')
        ]

        urls = [
            url for url in urls
            if url and url.startswith('https://groups.google.com/forum/')
        ]

        with open('urls.txt', 'w') as f:
            f.writeline('%s' % '\n'.join(urls))

        return urls

    def _save_content_of_messages(self, url):
        """ Save the content in the raw url provided.

        Persists the message to forum_name/thread_id/message_id.  Return the
        content of the message for convenience.

        """

        import requests
        from urlparse import urlsplit
        from os import makedirs
        from os.path import dirname, sep

        message = requests.get(url).text

        query = urlsplit(url).query
        query = dict([params.split('=') for params in query.split('&')])
        path = query['msg']

        file_path = path.replace('/', sep)
        dir_ = dirname(file_path)

        if not exists(dir_):
            makedirs(dir_)

        with open(file_path, 'w') as f:
            f.write(message.encode('utf8'))

        return message

    def _scroll_to_get_all_posts(self):
        """ Scroll the page until all the posts get displayed.

        Caution: Quite hackish!

        """

        print 'Scrolling until all the posts are visible ...'

        while True:
            if self.verbose:
                print 'scrolling...'

            last_post = self._get_last_post()

            def new_post_fetched(d):
                new_post = self._get_last_post()
                return last_post.text != new_post.text

            try:
                self.wait.until(lambda d: new_post_fetched(d))
            except TimeoutException:
                print 'Found all posts.'
                break

        return self._get_post_list()

if __name__ == "__main__":
    forum_url = 'https://groups.google.com/forum/#!forum/mumbai-ultimate'
    scraper = GoogleGroupsScraper(forum_url, verbose=True)
    scraper.save_all_posts()
