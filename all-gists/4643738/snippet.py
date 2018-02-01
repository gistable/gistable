"""An example of how to perform a multi-threaded unit test of a web service.

The particulars of this example make use of some conventions used when
developing a web service when using the Flask microframework, but can be
modified to fit most needs.
"""

import json
import threading
import time
import unittest

import requests

# Assume that we have some factory that setups and creates the (Flask)
# web service application
from myapp import create_app

# The URL to the REST API that we will start up. This is the default location
# where Flask apps start when using the built in web server.
SERVER_URL = "http://127.0.0.1:5000"

class WebServiceThreadingTestCase(unittest.TestCase):
    """A Test case to test the thread safety of a web service."""

    def setUp(self):
        """Setup to run before each test case."""
        # Use the factory method to create the app.
        self.app = create_app()

    def tearDown(self):
        """Teardown to run after each test case."""
        # If you use any sort of database connections to verify the contents
        # of the database that the REST server is updating, you can close them
        # here.
        pass

    def login(self, username, password):
        """Helper method to let us log in to our web service."""

        # Create a dictionary of login data
        login_data = json.dumps(dict(username=username, password=password))

        # Log in to our service
        return requests.post(SERVER_URL + "/login", data=login_data,
                                headers={'content-type': 'application/json'})

    def logout(self, cookies):
        """Helper method to let us log out from our web service."""
        return requests.post(SERVER_URL + "/logout", cookies=cookies)

    def runTest(self):
        """Run the actual threading test."""

        def start_and_init_server(app):
            """A helper function to start out server in a thread.

            This could be done as a lamnda function, but this way we can
            perform other setup functions if necessary.

            Args:
                app: The Flask app to run
            """
            app.run(threaded=True)

        # Create a thread that will contain our running server
        server_thread = Thread(target=start_and_init_server, args=(self.app, ))

        # The number of new posts to create
        n_new_posts = 50

        request_threads = []
        try:
            # Start the server
            server_thread.start()

            # Log in and keep the cookie that the service sends back.
            r = self.login('someuser', 'somepass')
            cookies = r.cookies

            # Get the number of existing posts for this user
            r = requests.get(SERVER_URL + "/posts/count", cookies=cookies)
            n_original_posts = int(r.json()['count'])

            def post_data():
                """Another helper function that will actually do all of the
                work of sendind data to the Flask app that we have running."""
                data = dict(
                        post_name='Some new post'
                        post_content='The content of my new blog post'
                    )
                
                # Make the actual request making sure that we pass the data,
                # the appropriate headers, and the cookies that were passed
                # use during the login phase
                r = requests.post(SERVER_URL + "/posts",
                                data=json.dumps(data),
                                headers={'content-type': 'application/json'},
                                cookies=cookies)
            
            # Create threads for all of the requests and start them
            for i in range(n_new_posts):
                t = Thread(target=post_data)
                request_threads.append(t)
                t.start()

            # Wait until all of the threads are complete
            all_done = False
            while not all_done:
                all_done = True
                for t in request_threads:
                    if t.is_alive():
                        all_done = False
                        time.sleep(1)

            # Check the make sure that all the posts are there
            # Get the number of existing posts for this user
            r = requests.get(SERVER_URL + "/posts/count")
            n_posts = int(r.json()['count'])

            # They better all be there!
            self.assertEqual(n_posts, n_original_posts + n_new_posts)

            # Log out of the system
            self.logout(cookies)
        except Exception, ex:
            print 'Something went horribly wrong!', ex.message
        finally:

            # Stop all running threads
            server_thread._Thread__stop()
            for t in request_threads:
                t._Thread__stop()
