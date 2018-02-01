"""Utility to clear our unused Django CMS placeholder data from database"""

# Nick Snell <n@nicksnell.com>

# WARNING; IS A DISTRUCTIVE OPERATION (Obviously.)

from django.template import TemplateDoesNotExist
from cms.models.pagemodel import Page
from cms.utils.plugins import get_placeholders


def seek_and_destroy(dryrun=False, debug=True):
	"""Find the page placeholders not longer in use and remove them. This is
	useful in situations where you change templates wholesale (v1 -> v2 etc)
	and need to clear out the chaff from the database"""

	# Go though each page, look at the placeholders in the page
	# template and compare to what it currently has.
	for page in Page.objects.all():
		try:
			template_placeholders = get_placeholders(page.get_template())
		except TemplateDoesNotExist:
			if debug:
				print '** "%s" has template "%s" which could not be found **' % (
					page.get_title(),
					page.template,
				)

			continue

		if debug:
			print '"%s" has %s placeholder(s):' % (
				page.get_title(),
				len(template_placeholders)
			)

		for placeholder in page.placeholders.all():
			if not placeholder.slot in template_placeholders:
				if debug:
					print '   "%s" has "%s" placeholder slot which is no longer in use' % (
						page.get_title(),
						placeholder.slot
					)

				# This placeholder is not welcome here.
				if not dryrun:
					page.placeholders.remove(placeholder)


if __name__ == '__main__':
	seek_and_destroy(dryrun=True)
