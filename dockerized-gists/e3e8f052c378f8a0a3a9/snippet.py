import re
import markdown2

class CustomMarkdown(markdown2.Markdown):
	"""
	Custom markdown processor that we use for task list
	"""

	reTaskList = re.compile('''
	(?P<prefix>[\r\n|\n|\r]*)
	-\s\[(?P<done>[x|\s]?)\]\s*(?P<item>.*)
	(?P<suffix>[\r\n|\n|\r]*)
	''', re.IGNORECASE | re.MULTILINE | re.VERBOSE)

	LIST_ITEM_TEMPLATE = '''
	<li class="md-task-item %s">
	  <label class="md-task-label">
		<input type="checkbox" %s>
		%s
	  </label>
	</li>
	'''

	def preprocess(self, text):

		def replace(match):
			item = match.groups()
			html = ''
			# The starting of the list if denoted by the first group having 2 or more newline chars
			if len(item[0]) >= 2:
				html += '\n<ul class="md-task-list">'

			# Now, toggle the checked status
			checked, klass = ('checked="checked"', 'completed') if item[1].lower() == 'x' else ('', 'pending')
			html += CustomMarkdown.LIST_ITEM_TEMPLATE % (klass, checked, item[2])

			# Similarly, check for ending
			if len(item[3]) >= 2:
				html += '</ul>\n'

			return html

		return CustomMarkdown.reTaskList.sub(replace, text)


def markdown(text, html4tags=False, tab_width=markdown2.DEFAULT_TAB_WIDTH,
			 safe_mode=None, extras=None, link_patterns=None,
			 use_file_vars=False):
	return CustomMarkdown(html4tags=html4tags, tab_width=tab_width,
					safe_mode=safe_mode, extras=extras,
					link_patterns=link_patterns,
					use_file_vars=use_file_vars).convert(text)


TEXT='''
Listify this!

- [ ] Some important task
- [x] A task that is already done
- [ ] Another thing for me to do

'''

print(markdown(TEXT))