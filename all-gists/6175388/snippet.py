'''
Kivy + Facebook SDK
===================

This example works only on Android.

Create debug hash key (default debug key password is `android`)::

    keytool -exportcert -alias androiddebugkey -keystore \ 
        ~/.android/debug.keystore  | openssl sha1 -binary | openssl base64

Available Facebook permissions:

    https://developers.facebook.com/docs/reference/fql/permissions/

Issues:

* W/fb4a:fb:OrcaServiceQueue(28514): com.facebook.orca.protocol.base.ApiException:
  The proxied app is not already installed.

  -> ?, doesn't seem dangerous.

'''


from kivy.properties import StringProperty, BooleanProperty
from kivy.event import EventDispatcher
from kivy.clock import Clock
from jnius import autoclass, PythonJavaClass, java_method, cast
from android import activity
from android.runnable import run_on_ui_thread


context = autoclass('org.renpy.android.PythonActivity').mActivity
Arrays = autoclass('java.util.Arrays')
Session = autoclass('com.facebook.Session')
SessionBuilder = autoclass('com.facebook.Session$Builder')
SessionOpenRequest = autoclass('com.facebook.Session$OpenRequest')
SessionNewPermissionsRequest = autoclass('com.facebook.Session$NewPermissionsRequest')
Request = autoclass('com.facebook.Request')


class _FacebookStatusCallback(PythonJavaClass):
    __javainterfaces__ = ['com.facebook.Session$StatusCallback']
    __javacontext__ = 'app'

    def __init__(self, fb):
        self.fb = fb
        super(_FacebookStatusCallback, self).__init__()

    @java_method('(Lcom/facebook/Session;Lcom/facebook/SessionState;Ljava/lang/Exception;)V')
    def call(self, session, state, exception):
        self.fb.status = state.toString()
        self.fb._update_state()


class _FacebookRequestCallback(PythonJavaClass):
    __javainterfaces__ = ['com.facebook.Request$Callback']
    __javacontext__ = 'app'

    def __init__(self, callback):
        self.callback = callback
        super(_FacebookRequestCallback, self).__init__()

    @java_method('(Lcom/facebook/Response;)V')
    def onCompleted(self, response):
        self.callback(response)


class _FacebookGraphUserCallback(PythonJavaClass):

    __javainterfaces__ = ['com.facebook.Request$GraphUserCallback']
    __javacontext__ = 'app'

    def __init__(self, callback):
        self.callback = callback
        super(_FacebookGraphUserCallback, self).__init__()

    @java_method('(Lcom/facebook/model/GraphUser;Lcom/facebook/Response;)V')
    def onCompleted(self, user, response):
        self.callback(user, response)


class Facebook(EventDispatcher):
    '''Facebook connector object. Permissions can be found at:

        https://developers.facebook.com/docs/reference/fql/permissions/

    '''

    status = StringProperty('')
    '''Return the current status of the facebook session.
    '''

    is_open = BooleanProperty(False)
    '''True if the session is ready to use.
    '''

    __events__ = ('on_open', 'on_closed')

    def __init__(self, app_id, permissions_read=['basic_info'],
            permissions_write=[]):
        super(Facebook, self).__init__()
        activity.bind(on_activity_result=self._on_activity_result)
        self._permissions_read = permissions_read
        self._permissions_write = permissions_write
        self._app_id = app_id
        self._session_callback = _FacebookStatusCallback(self)
        self._session = None
        self._requests = []

    def open(self):
        '''Open a facebook connection.
        When the session is opened, the event `on_open` will be fired.

        '''
        self._open_for_read()

    def on_open(self):
        '''Fired when the Facebook session is opened and ready to use.
        '''
        pass

    def on_closed(self, error):
        '''Fired when the Facebook session has been closed. An additionnal
        `error` message might be passed.
        '''
        pass

    @run_on_ui_thread
    def post(self, text, callback=None):
        '''Post a new message from the application to the user wall
        '''
        # Facebook said the asynchronous request must be run in the ui thread.
        # ref: https://developers.facebook.com/docs/reference/androidsdk/ayncrequest/
        req = None
        def _callback(*args):
            if callback:
                callback(*args)
            self._requests.remove(req)
        req = Request.newStatusUpdateRequest(
                self._session, text, _FacebookRequestCallback(_callback))
        self._requests.append(req)
        req.executeAsync()

    @run_on_ui_thread
    def me(self, callback):
        '''Get all the user information.
        '''
        req = None
        def _callback(*args):
            if callback:
                callback(*args)
            self._requests.remove(req)
        req = Request.newMeRequest(
                self._session, _FacebookGraphUserCallback(_callback))
        self._requests.append(req)
        req.executeAsync()

    #
    # private
    #

    def _update_state(self):
        status = self.status
        if status == 'OPENED':
            # read access is ok, now schedule the write access if needed
            Clock.schedule_once(self._open_for_write, 0)
        elif status == 'OPENED_TOKEN_UPDATED':
            # write access ok!
            self.is_open = True
            self.dispatch('on_open')
        elif status == 'CLOSED':
            self.is_open = False
            self.dispatch('on_closed', None)
        elif status == 'CLOSED_LOGIN_FAILED':
            self.is_open = False
            self.dispatch('on_closed', 'login failed')

    def _on_activity_result(self, requestCode, resultCode, data):
        # When the activity got a result, pass it to facebook for processing.
        self._session.onActivityResult(
            cast('android.app.Activity', context),
            requestCode, resultCode, data)

    def _open_for_read(self):
        self._session = Session.getActiveSession()
        if self._session:
            if self._session.isOpened():
                return
            if self._session.isClosed():
                self._session = None

        if not self._session:
            # more complex permission
            self._session = SessionBuilder(context).setApplicationId(self._app_id).build()
            Session.setActiveSession(self._session)
            self._session.addCallback(self._session_callback)

            self.req = SessionOpenRequest(cast('android.app.Activity', context))
            self.req.setPermissions(Arrays.asList(*self._permissions_read))
            self._session.openForRead(self.req)

        else:
            Clock.schedule_once(self._open_for_write, 0)

    def _open_for_write(self, *args):
        if not self._permissions_write:
            self.is_open = True
            self.dispatch('on_open')
            return

        self._session.requestNewPublishPermissions(
            SessionNewPermissionsRequest(
                cast('android.app.Activity', context),
                Arrays.asList(*self._permissions_write)))


if __name__ == '__main__':
    from kivy.app import App
    from kivy.lang import Builder

    kv = '''
BoxLayout:
    BoxLayout:
        orientation: 'vertical'
        Label:
            text: 'Facebook Status: [b]{}[/b]\\nMessage: [b]{}[/b]'.format(app.facebook.status, app.post_status)
            markup: True
            size_hint_y: None
            height: '48dp'

        Label:
            text: app.user_infos

        Button:
            text: 'Log into Facebook'
            size_hint_y: None
            height: '48dp'
            on_release: app.facebook.open()

        Button:
            text: 'Get user informations'
            size_hint_y: None
            height: '48dp'
            on_release: app.fb_me()

    BoxLayout:
        orientation: 'vertical'
        TextInput:
            id: ti
            text: 'Hello from Kivy + Facebook Android SDK'
        Button:
            text: 'Post to Facebook'
            on_release: app.fb_post(ti.text)
            size_hint_y: None
            height: '48dp'
    '''

    FACEBOOK_APP_ID = 'XXX REPLACE WITH YOUR APP ID XXX'

    class FacebookApp(App):

        post_status = StringProperty('-')
        user_infos = StringProperty('-')

        def build(self):
            self.facebook = Facebook(FACEBOOK_APP_ID,
                permissions_write=['publish_actions'])
            return Builder.load_string(kv)

        def fb_me(self):
            def callback(user, *args):
                infos = []
                infos.append('Name: {}'.format(user.getName()))
                infos.append('FirstName: {}'.format(user.getFirstName()))
                infos.append('MiddleName: {}'.format(user.getMiddleName()))
                infos.append('LastName: {}'.format(user.getLastName()))
                infos.append('Link: {}'.format(user.getLink()))
                infos.append('Username: {}'.format(user.getUsername()))
                infos.append('Birthday: {}'.format(user.getBirthday()))
                location = user.getLocation()
                if location:
                    infos.append('Country: {}'.format(location.getCountry()))
                    infos.append('City: {}'.format(location.getCity()))
                    infos.append('State: {}'.format(location.getState()))
                    infos.append('Zip: {}'.format(location.getZip()))
                    infos.append('Latitude: {}'.format(location.getLatitude()))
                    infos.append('Longitude: {}'.format(location.getLongitude()))
                else:
                    infos.append('No location available')

                self.user_infos = '\n'.join(infos)

            self.facebook.me(callback)

        def fb_post(self, text):
            def callback(*args):
                from time import time
                self.post_status = 'message posted at {}'.format(time())
            self.facebook.post(text, callback=callback)

        def on_pause(self):
            return True

    FacebookApp().run()
