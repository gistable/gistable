from django.template import Library
from django.template.defaulttags import URLNode, url
 
register = Library()
 
class AbsoluteURL(str):
	pass
 
class AbsoluteURLNode(URLNode):
	def render(self, context):
		asvar, self.asvar = self.asvar, None
		path = super(AbsoluteURLNode, self).render(context)
		request_obj = context['request']
		abs_url = AbsoluteURL(request_obj.build_absolute_uri(path))
		
		if not asvar:
			return str(abs_url)
		else:
			if path == request_obj.path:
				abs_url.active = 'active'
			else:
				abs_url.active = ''
			context[asvar] = abs_url
			return ''
			
			
@register.tag
def absurl(parser, token):
	node = url(parser, token)
	return AbsoluteURLNode(
		view_name=node.view_name,
		args=node.args,
		kwargs=node.kwargs,
		asvar=node.asvar
		)