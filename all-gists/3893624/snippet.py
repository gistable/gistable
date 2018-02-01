import webapp2
import jinja2
import os
import json
import logging
import re
import hashlib
import hmac
import random
import string
from time import strftime
from time import time
from google.appengine.ext import db
from google.appengine.api import memcache
import blog_main

PAGE_TITLE = "Blog"
PATH = '/blog'

#------------------------------------------------ blog-specific object classes ----------------------------------------------------
class Post(db.Model):
	author = db.StringProperty()
	title = db.StringProperty(required = True)
	body = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	last_modified = db.DateTimeProperty(auto_now = True)
	comments = db.IntegerProperty()
	
	def add_comment(self, author, body):
		self.comments += 1
		id = self.key().id()
		new = Comment(parent = self, author = author, body = body, post_id = id, number = self.comments)
		new.put()
		self.put()
		memcache.set(str(id), self)
		memcache.delete(str(id)+'_comments')
		
	def render(self, preview = False):
		self._render_text = self.body.replace('\n', '<br>')
		if preview and len(self._render_text) > 500:
			self._render_text = self._render_text[:499] + '... <a href = /blog/%s class = "top-link">read more</a>' % self.key().id()
		return blog_main.render_string('post.html', post = self)
		
class Comment(db.Model):
	author = db.StringProperty()
	body = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	last_modified = db.DateTimeProperty(auto_now = True)
	post_id = db.IntegerProperty(required = True)
	number = db.IntegerProperty(required = True)
	
	def render(self):
		#self._render_text = self.body.replace('\n', '<br>\n')
		return blog_main.render_string('comment.html', comment = self)
		
		
# ----------------------------------------------- code for displaying the blog -------------------------------------------------
class Handler(blog_main.Handler):
	def render_html(self, template, **kw):
		self.write(self.render_string(template, user = self.user, age = self.get_age(), page_title = PAGE_TITLE, path = PATH, **kw))
		
class BlogHandler(Handler):
	def get(self):
		posts = memcache.get('all')
		if posts is None:
			logging.error("DB QUERY")
			posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC")
			memcache.set('all', posts)
			memcache.set('last_queried', time())
		if self.request.url.endswith('.json'):
			self.response.headers['Content-Type'] = 'application/json'
			self.write(json.dumps([{'subject':post.title, 'content':post.body, 'created':strftime('%A, %B %c',post.created.timetuple())}
				for post in posts], {'Queried %s seconds ago.' % age}))
		else:
			self.render_html("front_template.html", posts = posts) 

			
def get_post(id):
	post = memcache.get(id)
	if post is None:
		logging.error("DB QUERY")
		key = db.Key.from_path('Post', int(id))
		post = db.get(key) 
		memcache.set(id, post)
		memcache.set('last_queried', time())
	return post
			

#id is passed from the RE that recognizes the url
class PostHandler(Handler):
	def get(self, id):
		post = get_post(id)
		comments = memcache.get(id + '_comments')
		if post:
			if comments is None:
				logging.error('COMMENT QUERY')
				comments = db.GqlQuery('select * from Comment where ancestor is :1 order by created asc', post)
				memcache.set(id + '_comments', comments)
			if self.request.url.endswith('.json'):
				self.response.headers['Content-Type'] = 'application/json'
				self.write(json.dumps({'subject':post.title, 'content':post.body, 'created':strftime('%A, %B %c',post.created.timetuple())}))
			else:
				self.render_html("permalink_template.html", post = post, comments = comments)
		else:
			self.render_html('404.html')
			
	def post(self, id):
		content = self.request.get("content")
		if content:
			post = get_post(id)
			author = self.user.username
			post.add_comment(author, content)
			self.redirect(self.request.get('path'))
		else:
			error = "you monster"
			self.render_form(content, error)
			
#---------------------------------------------- newpost --------------------------------------------------------------			
class NewPostHandler(Handler):
	def render_form(self, subject = "", content = "", error = ""):
		self.render_html("newpost_form.html", subject = subject, content = content , error = error)
	def get(self):
		if self.user and self.user.post_permission == True:
			self.render_form()
		else:
			self.redirect('/login')
	def post(self):
		subject = self.request.get("subject")
		content = self.request.get("content")
		if subject and content:
			p = Post(author = self.user.username, title = subject, body = content, comments = 0)
			p.put()										
			id = p.key().id()
			memcache.set(str(id), p)
			memcache.delete('all')
			self.redirect('/blog/' + str(id))
		else:
			error = "you monster"
			self.render_form(subject, content, error)


app = webapp2.WSGIApplication([
					(r'/blog/?', BlogHandler), 
					(r'/blog/\.(?:json)', BlogHandler), 
					(r'/blog/newpost', NewPostHandler), 
					(r'/blog/(\d+)', PostHandler),
					(r'/blog/(\d+)\.(?:json)', PostHandler),
					],
				debug=True)
