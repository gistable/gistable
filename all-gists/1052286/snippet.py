#!/usr/bin/env python

import cookielib
import json
import re
import random
import unittest

import requests
from wordpress_xmlrpc import Client, WordPressComment, WordPressPost
from wordpress_xmlrpc.methods.posts import EditPost, DeletePost, GetPost, NewPost
from wordpress_xmlrpc.methods.comments import EditComment, DeleteComment, NewComment

DOMAIN = 'chicagonow.dev'
USERNAME = 'admin'
PASSWORD = 'password'
TEST_BLOG = 'cta-tattler'

MAX_AGE_REGEX = re.compile('max-age\s*=\s*(\d+)')

def build_url(path):
    """
    Construct an absolute url by appending a path to a domain.
    """
    return 'http://%s%s' % (DOMAIN, path)

class TestCachingBase(unittest.TestCase):
    """
    Base class Wordpress + Varnish TestCases.

    Provides utils for login/logout and asserting hits/misses.
    """
    def login(self):
        """
        Login and return a cookie jar holding the login cookie.
        """
        cookies = cookielib.CookieJar()
        response = requests.post(
            build_url('/wp-admin/admin-ajax.php'),
            cookies=cookies,
            data = {
                'action': 'chicagonow',
                'url': 'users/login',
                'data': '{"user_email":"%s","user_pass":"%s"}' % (USERNAME, PASSWORD)
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertMiss(response)

        return cookies 

    def logout(self, cookies):
        """
        Logout and return a now-empty cookie jar.
        """
        response = requests.post(
            build_url('/wp-admin/admin-ajax.php'),
            cookies=cookies,
            data = {
                'action': 'chicagonow',
                'url': 'users/logout'
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertMiss(response) 

        response_json = json.loads(response.read())
        self.assertEqual(response_json['logged_out'], True)

        return cookies

    def get_xmlrpc(self, blog=None):
        """
        Fetch an XML-RPC client for a given blog (or the root blog).
        """
        if blog:
            path = '/%s/xmlrpc.php' % blog
        else:
            path = '/xmlrpc.php'

        return Client(build_url(path), USERNAME, PASSWORD)

    def new_post(self, blog):
        """
        Create a new post.
        """
        xmlrpc = self.get_xmlrpc(blog) 
        post = WordPressPost()
        post.title = 'New post from api'
        post.description = 'New description'
        return xmlrpc.call(NewPost(post, True))

    def edit_post(self, blog, post_id):
        """
        Edit a post.
        """
        xmlrpc = self.get_xmlrpc(blog)
        post = WordPressPost()
        post.title = 'Edited post from api'
        post.description = 'Edited description'
        return xmlrpc.call(EditPost(post_id, post, True))

    def delete_post(self, blog, post_id):
        """
        Delete a post.
        """
        xmlrpc = self.get_xmlrpc(blog)
        return xmlrpc.call(DeletePost(post_id))

    def get_post(self, blog, post_id):
        """
        Fetch a post object.
        """
        xmlrpc = self.get_xmlrpc(blog)
        return xmlrpc.call(GetPost(post_id))

    def new_comment(self, blog, post_id):
        """
        Create a new comment.
        """
        xmlrpc = self.get_xmlrpc(blog) 
        comment = WordPressComment()
        comment.content = 'Test comment from api. (%s)' % str(random.random() * 99999999)
        return xmlrpc.call(NewComment(post_id, comment))

    def edit_comment(self, blog, comment_id):
        """
        Edit a comment.
        """
        xmlrpc = self.get_xmlrpc(blog) 
        comment = WordPressComment()
        comment.content = 'Edited comment from api. (%s)' % str(random.random() * 99999999)
        return xmlrpc.call(EditComment(comment_id, comment))

    def delete_comment(self, blog, comment_id):
        """
        Delete a comment.
        """
        xmlrpc = self.get_xmlrpc(blog)
        return xmlrpc.call(DeleteComment(comment_id))

    def get_twice(self, url, **kwargs):
        """
        Fetch a url twice and return the second response (for testing cache hits).
        """
        requests.get(url, **kwargs)
        response = requests.get(url, **kwargs)

        return response

    def assertHit(self, response):
        """
        Assert that a given response contains the header indicating a cache hit.
        """
        self.assertEqual(response.headers['X-Cache'], 'Hit')

    def assertMiss(self, response):
        """
        Assert that a given response contains the header indicating a cache miss.
        """
        self.assertEqual(response.headers['X-Cache'], 'Miss')

    def assertMaxAge(self, response, value):
        """
        Assert that a given response contains the header indicating specific "max-age" value.
        """
        try:
            cache_control = response.headers['cache-control']
        except KeyError:
            try:
                cache_control = response.headers['Cache-Control']
            except:
                raise AssertionError('No cache-control header.')

        max_age = MAX_AGE_REGEX.match(cache_control)

        if not max_age:
            raise AssertionError('No max-age specified in cache-control header.')

        self.assertEqual(int(max_age.group(1)), value)

class TestLoggedIn(TestCachingBase):
    """
    Tests for logged-in users.
    """
    def setUp(self):
        self.cookies = self.login()

    def test_homepage(self):
        url = build_url('/')

        response = self.get_twice(url, cookies=self.cookies)

        self.assertHit(response)

    def test_post_preview(self):
        url = build_url('/2400-north1200-west/?p=4&preview=true&url=preview/4')

        response = requests.get(url, cookies=self.cookies)

        self.assertMiss(response)

class TestLoggedOut(TestCachingBase):
    """
    Tests for logged-out users.
    """
    def test_homepage(self):
        url = build_url('/')

        response = self.get_twice(url)

        self.assertHit(response)
        self.assertMaxAge(response, 300)

    def test_homepage_login_logout(self):        
        url = build_url('/')

        cookies = self.login()
        cookies = self.logout(cookies)

        response = self.get_twice(url, cookies=cookies)

        self.assertHit(response)

    def test_search(self):
        url = build_url('/search/')

        response = self.get_twice(url, params={ 'blog_s': 'test' })

        self.assertMiss(response)

    def test_static_content(self):
        url = build_url('/wp-content/themes/chicagonow/images/home-logo.png')

        response = self.get_twice(url)

        self.assertHit(response)
        self.assertMaxAge(response, 604800)

    def test_avatar(self):
        url = build_url('/avatar/user-1-16.png')

        response = self.get_twice(url)

        self.assertHit(response)
        self.assertMaxAge(response, 604800)

    def test_ajax_users(self):
        url = build_url('/wp-admin/admin-ajax.php')
        data = {
            'action': 'chicagonow',
            'url': 'users',
            'data': 'null'
        }

        response = self.get_twice(url, data=data)

        self.assertMiss(response)

    def test_ajax_comment_form(self):
        url = build_url('/wp-admin/admin-ajax.php')
        data = {
            'action': 'commentform',
            'data': '{ "post_id": 61 }'
        }

        response = self.get_twice(url, data=data)

        self.assertMiss(response)

    def test_new_post(self):
        url = build_url('/%s/' % TEST_BLOG)

        response = self.get_twice(url)
        self.assertHit(response)

        self.new_post(TEST_BLOG)

        response = requests.get(url)
        self.assertMiss(response)

    def test_edit_post(self):
        url = build_url('/%s/' % TEST_BLOG)

        post_id = self.new_post(TEST_BLOG)

        response = self.get_twice(url)
        self.assertHit(response)

        self.edit_post(TEST_BLOG, post_id)

        response = requests.get(url)
        self.assertMiss(response)

    def test_delete_post(self):
        url = build_url('/%s/' % TEST_BLOG)

        post_id = self.new_post(TEST_BLOG)

        response = self.get_twice(url)
        self.assertHit(response)

        self.delete_post(TEST_BLOG, post_id)

        response = requests.get(url)
        self.assertMiss(response)

    def test_preview_post(self):
        post_id = self.new_post(TEST_BLOG)
        post = self.get_post(TEST_BLOG, post_id)

        response = self.get_twice('%s?preview=true' % post.permalink)
        self.assertMiss(response)

    def test_new_comment(self):
        post_id = self.new_post(TEST_BLOG)
        post = self.get_post(TEST_BLOG, post_id)

        response = self.get_twice(post.permalink)
        self.assertHit(response)

        self.new_comment(TEST_BLOG, post_id)

        response = requests.get(post.permalink)
        self.assertMiss(response)

    def test_edit_comment(self):
        post_id = self.new_post(TEST_BLOG)
        post = self.get_post(TEST_BLOG, post_id)
        
        comment_id = self.new_comment(TEST_BLOG, post_id)

        response = self.get_twice(post.permalink)
        self.assertHit(response)

        self.edit_comment(TEST_BLOG, comment_id)

        response = requests.get(post.permalink)
        self.assertMiss(response)

    def test_delete_comment(self):
        post_id = self.new_post(TEST_BLOG)
        post = self.get_post(TEST_BLOG, post_id)
        
        comment_id = self.new_comment(TEST_BLOG, post_id)

        response = self.get_twice(post.permalink)
        self.assertHit(response)

        self.delete_comment(TEST_BLOG, comment_id)

        response = requests.get(post.permalink)
        self.assertMiss(response)

    def test_new_comments_purge_too_much(self):
        # Comments were incorrectly busting site root
        post_id = self.new_post(TEST_BLOG)

        url = build_url('/')

        response = self.get_twice(url)
        self.assertHit(response)

        self.new_comment(TEST_BLOG, post_id)

        response = requests.get(url)
        self.assertHit(response)

if __name__ == '__main__':
    unittest.main()
