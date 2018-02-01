# -*- coding: utf-8 -*-
from django.http import HttpResponseNotFound

class AdminSiteSecurizeMiddleware(object):
	"""Hide admin panel for unprivileged users"""
	def process_response(self, request, response):
		"""
		Return a 404 Not Found page if there is no authenticated user
		or if user has no enough privileges
		"""
		if '/admin/' in request.META.get("PATH_INFO"):
			if not request.user.is_authenticated() or not request.user.is_staff:
				return HttpResponseNotFound()
		return response