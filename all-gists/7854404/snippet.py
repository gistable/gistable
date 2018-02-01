from django import template
from django.utils.safestring import mark_safe
from django.core.exceptions import ObjectDoesNotExist
import re

register = template.Library()

@register.filter
def post_with_inline_images(post_instance):
    """
    Pass in a blog post instance (not just the body). This blog post must have a body and one or more associated images.
    """
    body = post_instance.body

    def insert_link(matchobj):
        """
        Replace a string of format <<<imgname$alt_text.css_class#some_id>>> with:
        <img src="/path/to/imgname" alt="alt_text" class="css_class" id="some_id" />
        """
        imgname = matchobj.group('imgname')
        try:
            imgurl = post_instance.blogimage_set.get(name__exact=imgname).image.url
        except ObjectDoesNotExist: # Print the harmless '<<<...>>>' pattern instead
            return matchobj.group(0)

        return '<img src="{0}" alt="{alt}" class="{class}" id="{id}" />'.format(
            imgurl, **matchobj.groupdict(''))

    return re.sub(
    r'''<<<(?P<imgname>[-\w]+)(\$(?P<alt>[-\w\s]+))?(\.(?P<class>[-\w\s]+))?(\#(?P<id>[-\w]+))?>>>''',
        insert_link, body, re.U)