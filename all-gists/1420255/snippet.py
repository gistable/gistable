  import unittest
  from pyramid import testing
  from paste.deploy.loadwsgi import appconfig
  
  from webtest import TestApp
  from mock import Mock
  
  from sqlalchemy import engine_from_config
  from sqlalchemy.orm import sessionmaker
  from app.db import Session
  from app.db import Entity  # base declarative object
  from app import main
  import os
  here = os.path.dirname(__file__)
  settings = appconfig('config:' + os.path.join(here, '../../', 'test.ini'))
  
  class BaseTestCase(unittest.TestCase):
      @classmethod
      def setUpClass(cls):
          cls.engine = engine_from_config(settings, prefix='sqlalchemy.')
          cls.Session = sessionmaker()
  
      def setUp(self):
          connection = self.engine.connect()
  
          # begin a non-ORM transaction
          self.trans = connection.begin()
  
          # bind an individual Session to the connection
          Session.configure(bind=connection)
          self.session = self.Session(bind=connection)
          Entity.session = self.session

  class UnitTestBase(BaseTestCase):
      def setUp(self):
          self.config = testing.setUp(request=testing.DummyRequest())
          super(UnitTestBase, self).setUp()
  
      def get_csrf_request(self, post=None):
          csrf = 'abc'
  
          if not u'csrf_token' in post.keys():
              post.update({
                  'csrf_token': csrf
              })
  
          request = testing.DummyRequest(post)
  
          request.session = Mock()
          csrf_token = Mock()
          csrf_token.return_value = csrf
  
          request.session.get_csrf_token = csrf_token
  
          return request



  class TestViews(UnitTestBase):
      def test_login_fails_empty(self):
          """ Make sure we can't login with empty credentials"""
          from app.accounts.views import LoginView
          self.config.add_route('index', '/')
          self.config.add_route('dashboard', '/')
  
          request = testing.DummyRequest(post={
              'submit': True,
          })
  
          view = LoginView(request)
          response = view.post()
          errors = response['errors']
  
          assert errors[0].node.name == u'csrf_token'
          assert errors[0].msg == u'Required'
          assert errors[1].node.name == u'Username'
          assert errors[1].msg == u'Required'
          assert errors[2].node.name == u'Password'
          assert errors[2].msg == u'Required'
  
  
      def test_login_succeeds(self):
          """ Make sure we can login """
          admin = User(username='sontek', password='temp', kind=u'admin')
          admin.activated = True
          self.session.add(admin)
          self.session.flush()
  
          from app.accounts.views import LoginView
          self.config.add_route('index', '/')
          self.config.add_route('dashboard', '/dashboard')
  
          request = self.get_csrf_request(post={
                  'submit': True,
                  'Username': 'sontek',
                  'Password': 'temp',
              })
  
          view = LoginView(request)
          response = view.post()
  
          assert response.status_int == 302


  class IntegrationTestBase(BaseTestCase):
      @classmethod
      def setUpClass(cls):
          cls.app = main({}, **settings)
          super(IntegrationTestBase, cls).setUpClass()
  
      def setUp(self):
          self.app = TestApp(self.app)
          self.config = testing.setUp()
          super(IntegrationTestBase, self).setUp()



  class TestViews(IntegrationTestBase):
      def test_get_login(self):
          """ Call the login view, make sure routes are working """
          res = self.app.get('/login')
          self.assertEqual(res.status_int, 200)
  
      def test_empty_login(self):
          """ Empty login fails """
          res = self.app.post('/login', {'submit': True})
  
          assert "There was a problem with your submission" in res.body
          assert "Required" in res.body
          assert res.status_int == 200
  
      def test_valid_login(self):
          """ Call the login view, make sure routes are working """
          admin = User(username='sontek', password='temp', kind=u'admin')
          admin.activated = True
          self.session.add(admin)
          self.session.flush()
  
          res = self.app.get('/login')
  
          csrf = res.form.fields['csrf_token'][0].value
  
          res = self.app.post('/login', 
              {
                  'submit': True,
                  'Username': 'sontek',
                  'Password': 'temp',
                  'csrf_token': csrf
              }
          )
  
          assert res.status_int == 302
