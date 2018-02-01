from django import template
register = template.Library()

@register.filter(name='urltoname')
def urltoname(value):
	"filter that extracts the filename from a URL"
	x = str(value)
	return x[x.rfind("/")+1:]
