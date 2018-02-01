from django.core import paginator
from django.core.paginator import EmptyPage, PageNotAnInteger

class Paginator(paginator.Paginator):
	def __len__(self):
		try:
			return super(Paginator, self).__len__()
		except TypeError:
			return self.object_list.count()
	
	def page(self, number):
		"Returns a Page object for the given 1-based page number."
		number = self.validate_number(number)
		bottom = (number - 1) * self.per_page
		top = bottom + self.per_page
		if top + self.orphans >= self.count:
			top = self.count
		return Page(self.object_list[bottom:top], number, self)

class Page(paginator.Page):
	def __init__(self, object_list, number, paginator):
		object_list = list(object_list)
		super(Page, self).__init__(object_list, number, paginator)
	
	def __len__(self):
		try:
			return super(Page, self).__len__()
		except TypeError:
			return self.object_list.count(True)
	
	def __getitem__(self, index):
		return self.object_list[index]