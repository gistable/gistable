# coding=utf-8

import urwid
import requests
import re
from hashlib import md5
import time
from bs4 import BeautifulSoup, NavigableString
import lxml.html

USER = ''
PASS = ''

KEY_ENTER        = ['enter', 'right']
KEY_BACK         = ['esc', 'backspace', 'left']
KEY_REFRESH      = ['r', 'f5']
KEY_TREEVIEW     = ['t']
KEY_AUTHOR_ONLY  = ['o']
KEY_SEARCH_THREAD= ['s']
KEY_SEARCH_LOCAL = ['/']
KEY_REPLY        = ['r']
KEY_REPLY_CONFIRM= ['ctrl r']

PALETTE = [
	#  name        foreground          background
	('header',     'white',            'dark gray'),
	('footer',     'white',            'dark gray'),
	('focus',      'white',            'black'),
	('odd',        'black',            'white'),
	('even',       'black',            'light gray'),		
	('image_odd',  'black, underline', 'white'),
	('image_even', 'black, underline', 'light gray'),
	('highlight',  'white',            'dark red')
]

class AttributeDict(dict): 
	__getattr__ = dict.__getitem__
	__setattr__ = dict.__setitem__

class Forum:
	HP_URL = 'https://www.hi-pda.com/forum/'
	LOGIN_URL = HP_URL + 'logging.php?action=login'
	LOGIN_SUBMIT_URL = HP_URL + 'logging.php?action=login&loginsubmit=yes'
	DISPLAY_URL = HP_URL + 'forumdisplay.php?fid=2&page=%d'
	THREAD_URL = HP_URL + 'viewthread.php?tid=%d&page=%d'
	SEARCH_URL = HP_URL + 'search.php?srchtype=title&srchtxt=%s&searchsubmit=true&orderby=lastpost&ascdesc=desc&srchfid[0]=2&page=%d'
	POST_URL = HP_URL + 'post.php?action=%s'

	THREAD_RE = re.compile("normalthread_([0-9]+)")
	TID_RE = re.compile("viewthread.php\?tid=([0-9]+)")
	USER_RE = re.compile("space.php\?uid=([0-9]+)")
	POST_RE = re.compile("post_([0-9]+)")
	POST_DATE_RE = re.compile(u'发表于 ([\w\W]+)')
	RECORDS_RE = re.compile(u'相关主题 ([0-9]+) 个')

	THREAD_DATE_FORMAT = '%Y-%m-%d'
	REPLY_DATE_FORMAT = '%Y-%m-%d %H:%M'


	def __init__(self, username, password):
		self.username = username
		self.password = md5(password).hexdigest()
		self.session = requests.Session()
		self.session.headers.update({'User-Agent': 'D-Term'})

	def login(self):
		r = self.session.get(Forum.LOGIN_URL)
		formhash = re.compile('<input\s*type="hidden"\s*name="formhash"\s*value="([\w\W]+?)"\s*\/>').search(r.text).group(1)

		params = {
			"formhash": formhash,
			"loginfield": "username",
			"loginsubmit": True,
			"username": self.username.decode('utf-8').encode('gbk'),
			"password": self.password,
			"questionid": "0",
			"answer": "",
			"referer": "index.php",
		}
		r = self.session.post(Forum.LOGIN_SUBMIT_URL, params=params)
		if 'logging.php?action=login' in r.text:
			return False
		else:
			return True

	@staticmethod
	def parse_thread(thread_html):
		title = thread_html.find("th", class_="subject")
		author = thread_html.find("td", class_="author")
		nums = thread_html.find("td", class_="nums")
		lastpost = thread_html.find("td", class_="lastpost")

		return AttributeDict({
			'title': title.a.text,
			'id': int(Forum.TID_RE.search(title.a['href']).group(1)),
			'date': time.strptime(author.em.text, Forum.THREAD_DATE_FORMAT),
			'replys': int(nums.strong.text),
			'reviews': int(nums.em.text),
			'lastpost': AttributeDict({
				'author': lastpost.cite.a.text,
				'date': time.strptime(lastpost.em.a.text, Forum.REPLY_DATE_FORMAT),
			}),
			'author': AttributeDict({
				'id': int(Forum.USER_RE.match(author.cite.a['href']).group(1)),
				'name': author.cite.a.text
			})
		})

	def display(self, page=1):
		r = self.session.get(Forum.DISPLAY_URL % page)
		page = BeautifulSoup(r.content, "lxml", from_encoding="gb18030")

		records = int(page.find("div", id="forumheader").strong.text)

		pages = 1
		next = page.find("a", class_="next")
		if next:
			pages = next.previous_sibling.text
			pages = int(re.compile("([0-9]+)").search(pages).group(1))

		threads = []
		for thread in page.find_all("tbody", id=Forum.THREAD_RE):
			threads.append(Forum.parse_thread(thread))

		return records, pages, threads

	def search(self, title, page=1):
		r = self.session.get(Forum.SEARCH_URL % (title, page))
		page = BeautifulSoup(r.content, "lxml", from_encoding="gb18030")

		pages = 1
		next = page.find("a", class_="next")
		if next:
			pages = next.previous_sibling.text
			pages = int(re.compile("([0-9]+)").search(pages).group(1))
		records = Forum.RECORDS_RE.search(page.find("div", class_="itemtitle").em.text)
		if records:
			records = int(records.group(1))
		else:
			return pages, 0, []

		threads = []
		for thread in page.find("table", class_="datatable").find_all("tbody"):
			threads.append(Forum.parse_thread(thread))

		return pages, records, threads

	def viewthread(self, tid, page=1, authorid=None):
		author_only = ""
		if authorid:
			author_only = "&authorid=%d" % authorid
		r = self.session.get(Forum.THREAD_URL % (tid, page) + author_only)
		page = BeautifulSoup(r.content, "lxml", from_encoding="gb18030")
		html = lxml.html.fromstring(r.content.decode('gb18030'))

		pages = 1
		pages_div = page.find("div", class_="pages")
		if pages_div:
			next = pages_div.find("a", class_="next")
			if next:
				pages = next.previous_sibling.text
				pages = int(re.compile("([0-9]+)").search(pages).group(1))
			else:
				pages = int(pages_div.strong.text)

		posts = []
		for post in page.find_all("div", id=Forum.POST_RE):
			author = post.find("td", class_="postauthor")
			content = post.find("td", class_="t_msgfont")

			id = int(Forum.POST_RE.match(post['id']).group(1))
			level = int(post.find("a", id="postnum%d" % id).em.text)
			date = post.find("div", class_="authorinfo").em.text
			date = time.strptime(Forum.POST_DATE_RE.match(date).group(1), Forum.REPLY_DATE_FORMAT)

			msg = html.xpath("//div[@id='%s']//td[@class='t_msgfont']" % post['id'])
			message = ""
			images = []
			if len(msg) == 0:
				message = "作者被禁止或删除 内容自动屏蔽"
			else:
				msg = msg[0]
				reply = None
				if msg.text:
					message = msg.text.strip(' \r')
				for line in msg:
					if line.tag == 'i' and 'pstatus' in line.attrib.values(): None                  #本帖最后XXX编辑
					elif line.tag == 'div' and 'quote' in line.attrib.values():                     #引用
						rly = line.xpath(".//blockquote/font[@size='2']/a")
						if len(rly) > 0:
							match = re.compile("pid=([0-9]+)").search(rly[0].attrib['href'])
							if match:
								reply = int(match.group(1))
					elif line.tag == 'img':                                                         #图片
						if 'smilieid' not in line.attrib:											#表情
							if 'file' in line.attrib:
								images.append(Forum.HP_URL + line.attrib['file'])
							elif 'src' in line.attrib:
								images.append(line.attrib['src'])
					elif line.tag == 'span' and 'id' in line.attrib: continue                       #下载
					elif line.tag == 'div' and 't_attach' in line.attrib: None                      #下载
					elif line.tag == 'strong' and line.text and u'回复' in line.text:               #回复
						rly = line.xpath(".//a[@target='_blank']")
						if len(rly) > 0:
							reply = int(re.compile("pid=([0-9]+)").search(rly[0].attrib['href']).group(1))
					elif line.tag == 'script' or line.tag == 'embed': None                          #flash
					elif line.tag == 'a':                                                           #链接
						message += line.text_content().strip(' \r') + ' '
					elif line.tag == 'br':
						if line.text: message += line.text.strip(' \r')
					elif not line.tail:
						message += line.text_content().strip(' \r') + "\n"
					if line.tail:
						message += line.tail.strip(' \r')

			posts.append(AttributeDict({
				'level': level,
				'author': AttributeDict({
					'name': author.a.text,
					'id': int(Forum.USER_RE.match(author.a['href']).group(1)),
				}),
				'content': message.strip(),
				'id': id,
				'images': images,
				'date': time.strftime("%H:%M", date),
				'reply': reply
			}))

		return pages, posts

	def reply(self, msg, tid):
		reply_url = self.POST_URL%'reply' + '&fid=2&tid=%d'%tid
		r = self.session.get(reply_url)
		formhash = re.compile('<input\s*type="hidden"\s*name="formhash"\s*id="formhash"\s*value="([\w\W]+?)"\s*\/>').search(r.text).group(1)
		params = {
			'formhash': formhash,
			'posttime': str(int(time.time())),
			'noticeauthor': '',
			'noticetrimstr': '',
			'noticeauthormsg': '',
			'subject': '',
			'message': msg,
			'usesig': 1
		}
		r = self.session.post(reply_url + '&replysubmit=yes', params=params)
		page = BeautifulSoup(r.content, "lxml", from_encoding="gb18030")
		alert = page.find('div', class_="alert_info")
		if alert:
			return False
		return True

class ThreadListWalker(urwid.ListWalker):
	layout = AttributeDict({
		'level': 0,
		'name': 2,
		'title': 6
	})

	def __init__(self, title, on_next_page):
		self.highlight = title
		self.focus = 0
		self.page = 0
		self.on_next_page = on_next_page
		self.title = title
		self.threads = []
		self.thread_widgets = []
		self.count = 0

		self.page += 1
		self.records, self.pages, threads = self.on_next_page(self.title, self.page)
		self.append(threads)

	def append(self, threads):
		self.threads += threads
		for thread in threads:
			self.count += 1
			style = ["even", "odd"][self.count%2]
			findout, name = DTerm.make_highlight(thread.author.name, self.highlight)
			findout, title = DTerm.make_highlight(thread.title, self.highlight)

			self.thread_widgets.append(urwid.AttrMap(urwid.Columns([
				(3, urwid.Padding(urwid.Text(u"%3d" % self.count), align='right', width='pack')),
				(1, urwid.Text('|')),
				('weight', 1, urwid.Padding(urwid.Text(name, wrap="clip"), align='right', width='pack')),
				(1, urwid.SelectableIcon('|')),
				(4, urwid.Text(u'%4d' % thread.replys)),
				(1, urwid.Text('|')),
				('weight', 9, urwid.Text(title, wrap="clip")),
			], 1), style, 'focus'))

	def set_focus(self, focus):
		self.focus = focus

	def get_focus(self):
		if len(self.thread_widgets) == 0:
			return None, None
		return self.thread_widgets[self.focus], self.focus

	def get_next(self, position):
		if position < len(self.thread_widgets) - 1:
			focus = position+1
			self.thread_widgets[focus]._selectable = True
			return self.thread_widgets[focus], focus
		elif position == len(self.thread_widgets) - 1:
			if self.page < self.pages:
				self.page += 1
				self.records, self.pages, threads = self.on_next_page(self.title, self.page)
				self.append(threads)

				focus = position+1
				return self.thread_widgets[focus], focus
		return None, None

	def get_prev(self, position):
		if position > 0:
			focus = position-1
			return self.thread_widgets[focus], focus
		return None, None

	def set_highlight(self, text):
		first_find = -1
		self.highlight = text
		for i in range(0, len(self.threads)):
			thread = self.threads[i]
			thread_widget = self.thread_widgets[i].original_widget

			name = thread.author.name
			findout, highlight = DTerm.make_highlight(name, text)
			if findout and first_find == -1:
				first_find = i
			name_widget, options = thread_widget.contents[self.layout.name]
			name_widget = name_widget.original_widget
			name_widget.set_text(highlight)

			title = thread.title
			findout, highlight = DTerm.make_highlight(title, text)
			if findout and first_find == -1:
				first_find = i
			title_widget, options = thread_widget.contents[self.layout.title]
			title_widget.set_text(highlight)

		if first_find != -1:
			self.set_focus(first_find)

class ImageWidget(urwid.SelectableIcon):
	def __init__(self, url, style):
		self.url = url
		urwid.SelectableIcon.__init__(self, (style, u"[有图片]～"))

	def keypress(self, size, key):
		if key in KEY_ENTER:
			DTerm.self.turn_image(self.url)
		return key

class PostWidget(urwid.TreeWidget):
	indent_cols = 2

	layout = AttributeDict({
		'level': 0,
		'name': 2,
		'content': 4
	})

	@staticmethod
	def make_widget(post, order, indent=0, highlight=''):
		style = ["even", "odd"][order%2]
		image_style = ["image_even", "image_odd"][order%2]

		widget = urwid.AttrMap(urwid.Columns([
			(3, urwid.Padding(urwid.Text(u"%3d" % post.level), align='right', width='pack')),
			(1, urwid.Text('|')),
			(10-indent, urwid.Padding(urwid.Text(post.author.name, wrap="clip"), align='right', width='pack')),
			(1, urwid.Text('|')),
			urwid.Pile([urwid.Text(post.content)] + [ImageWidget(image, image_style) for image in post.images]),
			(5, urwid.Padding(urwid.Text(post.date, wrap="clip"), align='left', width='pack'))
		], 1), style)
		PostWidget.set_highlight(widget.original_widget, post, highlight)
		return widget

	@staticmethod
	def set_highlight(widget, post, text):
		findout = False
		name = post.author.name
		find, highlight = DTerm.make_highlight(name, text)
		if find:
			findout = True
		name_widget, options = widget.contents[PostWidget.layout.name]
		name_widget = name_widget.original_widget
		name_widget.set_text(highlight)

		content = post.content
		findout, highlight = DTerm.make_highlight(content, text)
		if find:
			findout = True
		content_widget, options = widget.contents[PostWidget.layout.content]
		content_widget, options = content_widget.contents[0]
		content_widget.set_text(highlight)

		return findout

	def load_inner_widget(self, indent=0):
		post = self._node._value
		return PostWidget.make_widget(post, post.order, indent)

	def get_indent_cols(self):
		depth = self.get_node().get_depth()
		if depth > 0:
			depth = depth - 1
		return self.indent_cols * depth

	def get_indented_widget(self):
		indent_cols = self.get_indent_cols()
		widget = self.load_inner_widget(indent_cols)
		return urwid.Padding(widget, width=('relative', 100), left=indent_cols)

	def selectable(self):
		post = self._node._value
		return len(post.images) > 0

class PostNode(urwid.ParentNode):
	def __init__(self, post, parent=None):
		if parent:
			parent.set_child_node(post.id, self)
		urwid.ParentNode.__init__(self, post, key=post.id, parent=parent)

	def load_child_keys(self):
		keys = self._children.keys()
		if keys:
			keys.sort()
		return keys

	def load_child_node(self, key):
		return self._children[key]

	def load_widget(self):
		return PostWidget(self)

class PostListWalker(urwid.ListWalker):
	def goto_last(self):
		newposts = []
		self.page = 0
		while self.page < self.pages:
			self.page += 1
			self.pages, posts = self.on_next_page(self.tid, self.page, self.authorid)
			newposts += posts
		newposts = newposts[len(self.posts):]
		self.append(newposts)
		self.set_focus(len(self.post_widgets)-1)
		self._modified()

	def __init__(self, tid, on_next_page, authorid=None):
		self.highlight = ''
		self.tid = tid
		self.authorid = authorid
		self.on_next_page = on_next_page

		self.page = 0
		self.focus = 0
		self.posts = []
		self.post_widgets = []

		self.page += 1
		self.pages, posts = self.on_next_page(self.tid, self.page, self.authorid)
		self.append(posts)

	def append(self, posts):
		self.posts += posts
		for post in posts:
			self.post_widgets.append(PostWidget.make_widget(post, post.level, highlight=self.highlight))

	def set_focus(self, focus):
		self.focus = focus

	def get_focus(self):
		return self.post_widgets[self.focus], self.focus

	def get_next(self, position):
		if position < len(self.post_widgets) - 1:
			focus = position+1
			return self.post_widgets[focus], focus
		elif position == len(self.post_widgets) - 1:
			if self.page < self.pages:
				self.page += 1
				self.pages, posts = self.on_next_page(self.tid, self.page, self.authorid)
				self.append(posts)

				focus = position+1
				return self.post_widgets[focus], focus
		return None, None

	def get_prev(self, position):
		if position > 0:
			focus = position-1
			return self.post_widgets[focus], focus
		else:
			return None, None

	def set_highlight(self, text):
		self.highlight = text
		first_find = -1
		for i in range(0, len(self.posts)):
			post = self.posts[i]
			post_widget = self.post_widgets[i].original_widget
			if PostWidget.set_highlight(post_widget, post, text) and first_find == -1:
				first_find = i

		if first_find != -1:
			self.set_focus(first_find)

	def tint(self, root):
		root.get_value().order = self.order
		self.order += 1
		for child in root.get_child_keys():
			self.tint(root.get_child_node(child))

	def make_tree(self):
		nodes = {}
		root = None

		for post in self.posts:
			if post.reply == None:
				parent=root
			else:
				parent=nodes[post.reply]

			node = PostNode(post, parent=parent)
			nodes[post.id] = node
			if root is None:
				root = node

		self.order = 1
		self.tint(root)

		return root


class ReplyWidget(urwid.Edit):
	time = time.time()
	def keypress(self, size, key):
		key = urwid.Edit.keypress(self, size, key)
		if key not in ['left', 'right']:
			return key

class DTerm:

	back_stack = []

	def __init__(self):
		DTerm.self = self
		self.state = "login"
		self.state_machine = AttributeDict({
			'transition': {
				"home": AttributeDict(
					zip(KEY_REFRESH, ["home"]*len(KEY_REFRESH)) +
					zip(KEY_BACK, ["back"]*len(KEY_BACK)) +
					zip(KEY_ENTER, ["post"]*len(KEY_ENTER)) +
					zip(KEY_SEARCH_LOCAL, ["search_local"]*len(KEY_SEARCH_LOCAL)) +
					zip(KEY_SEARCH_THREAD, ["search_thread"]*len(KEY_SEARCH_THREAD))
				),
				"post": AttributeDict(
					zip(KEY_BACK, ["back"]*len(KEY_BACK)) +
					zip(KEY_TREEVIEW, ["tree"]*len(KEY_TREEVIEW)) +
					zip(KEY_AUTHOR_ONLY, ["author_only"]*len(KEY_AUTHOR_ONLY)) +
					zip(KEY_SEARCH_LOCAL, ["search_local"]*len(KEY_SEARCH_LOCAL)) +
					zip(KEY_REPLY, ["reply"]*len(KEY_REPLY))
				),
				"author_only": AttributeDict(
					zip(KEY_BACK, ["back"]*len(KEY_BACK)) +
					zip(KEY_AUTHOR_ONLY, ["post"]*len(KEY_AUTHOR_ONLY))
				),
				"tree": AttributeDict(
					zip(KEY_BACK, ["back"]*len(KEY_BACK)) +
					zip(KEY_TREEVIEW, ["post"]*len(KEY_TREEVIEW))
				),
				"image": AttributeDict(
					zip(KEY_BACK, ["back"]*len(KEY_BACK))
				),
				"search_local": AttributeDict(
					zip(KEY_ENTER, ["highlight"]*len(KEY_ENTER)) +
					zip(KEY_BACK, ["back"]*len(KEY_BACK))
				),
				"search_thread": AttributeDict(
					zip(KEY_ENTER, ["home"]*len(KEY_ENTER)) +
					zip(KEY_BACK, ["back"]*len(KEY_BACK))
				),
				"reply": AttributeDict(
					zip(KEY_REPLY_CONFIRM, ["post"]*len(KEY_REPLY_CONFIRM)) +
					zip(KEY_BACK, ["back"]*len(KEY_BACK))
				),
			},
			'trigger': AttributeDict({
				"home": AttributeDict({
					'home': self.refresh,
					'back': self.turn_back,
					'post': self.viewthread,
					"search_local": self.turn_search_local,
					"search_thread": self.turn_search_thread
				}),
				"post": AttributeDict({
					'back': self.turn_back,
					'tree': self.turn_tree,
					"author_only": self.turn_author,
					"search_local": self.turn_search_local,
					"reply": self.turn_reply
				}),
				"author_only": AttributeDict({
					'back': self.turn_back,
					'post': self.turn_post
				}),
				"tree": AttributeDict({
					'back': self.turn_back,
					'post': self.turn_post,
				}),
				"image": AttributeDict({
					'back': self.turn_back,
				}),
				"search_local": AttributeDict({
					'highlight': self.turn_highlight,
					'back': self.turn_back,
				}),
				"search_thread": AttributeDict({
					'home': self.start_search,
					'back': self.turn_back,
				}),
				"reply":  AttributeDict({
					'post': self.confirm_reply,
					'back': self.turn_back,
				}),
			})
		})

		self.splash = urwid.BigText(u"Discovery", urwid.font.Thin6x6Font())
		self.splash = urwid.Padding(self.splash, 'center', width='clip')
		self.splash = urwid.Filler(self.splash, 'middle')

		self.home = urwid.Frame(self.splash)

		self.threads = []
		self.forum = Forum(USER, PASS)

		self.header = urwid.AttrMap(urwid.Columns([
			(3, urwid.Padding(urwid.Text(u"#"), align='right', width='pack')),
			(1, urwid.Text('|')),
			('weight', 1, urwid.Padding(urwid.Text(u"作者"), align='right', width='pack')),
			(1, urwid.Text('|')),
			(4, urwid.Text(u'回复')),
			(1, urwid.Text('|')),
			('weight', 9, urwid.Text(u"标题")),
		], 1), 'header')

		DTerm.loop = urwid.MainLoop(self.home, PALETTE, unhandled_input=self.onKeyDown, handle_mouse=False)
		DTerm.loop.set_alarm_in(0, self.onStart, self.home)
		DTerm.loop.run()

	@staticmethod
	def make_highlight(origin_text, search_text):
		highlight = ['']
		findout = False
		for word in re.split('(%s)' % search_text, origin_text):
			if word == search_text:
				findout = True
				word = ('highlight', word)
			if word != '':
				highlight.append(word)
		return findout, highlight

	def update_status(self, status):
		self.home.footer = urwid.AttrMap(urwid.Columns([
			(urwid.Text(status)),
			(16, urwid.Padding(urwid.Text(self.forum.username), align='right', width='pack'))
		]), 'footer')
		DTerm.loop.draw_screen()

	def refresh(self):
		self.home.body = self.splash
		self.threads = []
		self.listwalker = ThreadListWalker('', self.on_thread_next_page)
		self.home.body = urwid.ListBox(self.listwalker)

	def start_search(self):
		self.home.body = self.splash
		self.update_status(u'正在搜索...')

		text = self.search.edit_text
		self.listwalker = ThreadListWalker(text, self.on_search_next_page)

		self.home.body = urwid.ListBox(self.listwalker)
		self.update_status(u'搜索完成，相关主题%d个' % self.listwalker.records)

		self.home.set_focus("body")

	def viewthread(self):
		self.self.backup_state()

		widget, index = self.home.body.get_focus()
		self.thread = self.listwalker.threads[index]

		self.listwalker = PostListWalker(self.thread.id, self.on_post_next_page)

		self.home.header = urwid.AttrMap(urwid.Columns([
			(3, urwid.Padding(urwid.Text(u"#"), align='right', width='pack')),
			(1, urwid.Text('|')),
			(10, urwid.Padding(urwid.Text(u"作者"), align='right', width='pack')),
			(1, urwid.Text('|')),
			urwid.Text(self.thread.title, wrap="clip"),
			(5, urwid.Padding(urwid.Text(u"时间"), align='left', width='pack')),
		], 1), 'header')

		self.postbody = urwid.ListBox(self.listwalker)
		self.home.body = self.postbody
		self.authorbody = None
		DTerm.loop.draw_screen()

	def turn_image(self, url):
		self.self.backup_state()

		import aalib
		from PIL import Image
		from cStringIO import StringIO

		self.update_status(u'正在载入...')

		cols, rows = DTerm.loop.screen.get_cols_rows()
		(head_rows, foot_rows),(orig_head, orig_foot) = self.home.frame_top_bottom((cols, rows), False)
		rows -= head_rows + foot_rows

		r = self.forum.session.get(url)
		fp = StringIO(r.content)

		image = Image.open(fp).convert('L')
		origin_width, origin_height = image.size

		origin_width = origin_width * 2
		width_ratio = float(origin_width) / cols
		height_ratio = float(origin_height) / rows
		ratio = width_ratio if width_ratio > height_ratio else height_ratio

		width = int(origin_width / ratio)
		height = int(origin_height / ratio)
		screen = aalib.AsciiScreen(width=width, height=height)

		image = image.resize(screen.virtual_size)
		screen.put_image((0, 0), image)

		self.update_status(u'载入完成')

		widget = urwid.Filler(urwid.Padding(urwid.Text(screen.render()), align="center", width="pack"))
		self.state = "image"
		self.home.body = widget

	def turn_post(self):
		self.home.body = self.postbody

	def turn_author(self):
		if self.authorbody is None:
			authorid = self.thread.author.id
			self.home.body = urwid.ListBox(PostListWalker(self.thread.id, self.on_post_next_page, authorid))
			self.authorbody = self.home.body
		else:
			self.home.body = self.authorbody
		DTerm.loop.draw_screen()

	def turn_tree(self):
		self.home.body = urwid.TreeListBox(urwid.TreeWalker(self.listwalker.make_tree()))

	def turn_search_local(self):
		self.self.backup_state()
		self.search = urwid.Edit(u"/")
		self.home.footer = urwid.AttrMap(self.search, "footer")
		self.home.set_focus("footer")

	def turn_search_thread(self):
		self.backup_state()
		self.search = urwid.Edit(u"搜索: ")
		self.home.footer = urwid.AttrMap(self.search, "footer")
		self.home.set_focus("footer")

	def turn_highlight(self):
		text = self.search.edit_text
		self.listwalker.set_highlight(text)
		self.turn_back()

	def turn_reply(self):
		self.backup_state()
		self.reply = ReplyWidget(u'回复: ', multiline=True)
		self.home.footer = urwid.AttrMap(self.reply, "footer")
		self.home.set_focus('footer')

	def confirm_reply(self):
		msg = self.reply.edit_text
		tid = self.thread.id

		self.update_status(u'正在回复...')
		self.forum.reply(msg.encode('gbk'), tid)
		self.turn_back()
		self.listwalker.goto_last()

	def backup_state(self):
		self.back_stack.append((self.state, self.listwalker, self.home.header, self.home.body, self.home.footer))

	def turn_back(self):
		if len(self.back_stack) > 0:
			self.next_state, self.listwalker, self.home.header, self.home.body, self.home.footer = self.back_stack.pop()
			self.home.set_focus("body")
		else:
			self.next_state = self.state

	def on_thread_next_page(self, title, page):
		self.update_status(u'正在载入...')
		records, pages, threads = self.forum.display(page)
		self.update_status(u'载入完成')

		return records, pages, threads

	def on_search_next_page(self, title, page):
		self.update_status(u'正在载入...')
		pages, records, threads = self.forum.search(title.encode('gbk'), page)
		self.update_status(u'载入完成')

		return records, pages, threads

	def on_post_next_page(self, tid, page, authorid):
		self.update_status(u'正在载入...')
		pages, posts = self.forum.viewthread(tid, page, authorid)
		self.update_status(u'载入完成')

		return pages, posts

	def onStart(self, loop, home):
		self.update_status(u'正在登陆...')

		if self.forum.login():
			self.home.header = self.header
			self.refresh()
		else:
			self.update_status(u'登陆失败')

		self.state = "home"

	def onKeyDown(self, key):
		if key in self.state_machine.transition[self.state]:
			self.next_state = self.state_machine.transition[self.state][key]
			trigger = self.state_machine.trigger[self.state][self.next_state]
			trigger()
			self.state = self.next_state

term = DTerm()
