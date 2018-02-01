(r'^articles/(?P<year>\d{4}/?$, 'main.views.year'),

# When a use case comes up that a month needs to be involved as
# well, you add an argument in your regex:

(r'^articles/(?P<year>\d{4}/(?P<month>\d{2})/?$, 'main.views.year_month'),

# That works fine, unless of course you want to show something
# different for just the year, in which case the following case can be
# used, making separate views based on the arguments as djangoproject
# suggests (http://docs.djangoproject.com/en/dev/topics/http/urls/)

urlpatterns = patterns('',
    (r'^articles/(?P<year>\d{4})/$', 'news.views.year_archive'),
    (r'^articles/(?P<year>\d{4})/(?P<month>\d{2})/$', 'news.views.month_archive'),
    (r'^articles/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d+)/$', 'news.views.article_detail'),
)

# However it would be nice if we could make one pattern for one
# view with optional arguments. Luckily the django url reversing
# engine allows this, and we can do the following:

url(r'''^community/(?P<base_slug>[^/]+)/?(?P<school_slug>[^/]+)?/?(?P<grade_slug>[^/]+)?/?(?P<class_slug>      [^/]+)?$''',
    'changer.socialschools.posts.views.show_community',
    name="community"),

# This works fine when calling the url, but reversing will cause a 
# problem because django will treat the backslashes as optional and
# not include them in the reversed url, causing munged urls:

# community/base/schoolgradeclass

# To counter this we can alter the regex as follows, by making the
# '/' dependent on the presence of the corresponding slug. We make
# sure not to group this by adding (?:) so as not to pollute the
# django reversing engine with unnecessary arguments and at the 
# same time keeping the arguments optional:

    url(r'''^community(?:\/(?P<base_slug>[^/]+))'''
                          r'''(?:\/(?P<school_slug>[^/]+))?'''
                          r'''(?:\/(?P<grade_slug>[^/]+))?'''
                          r'''(?:\/(?P<class_slug>[^/]+))?$''',
       'changer.socialschools.communities.views.this_community',
       name="community-view"),

# This makes it work with one url pattern. But what if we want to
# make a pattern for recent news in that a particular community, 
# such as news in a particular grade or school? We can add an 
# negative lookahead assertion:

url(r'''^community/(?P<base_slug>[^/]+)'''
                 r'''(?:\/(?P<school_slug>(?!recent)[^/]+))?'''
                 r'''(?:\/(?P<grade_slug>(?!recent)[^/]+))?'''
                 r'''(?:\/(?P<class_slug>(?!recent)[^/]+))?/recent/?$''',
    'changer.socialschools.communities.views.show_recent',
    name="community-recent"),


# This makes the following possible:

"""
>>> from django.core.urlresolvers import resolve
>>> resolve('/community/base/school/grade/class/recent')

ResolverMatch(func=<function show_recent at 0x103097d70>, args=(), kwargs={'class_slug': 'class', 'base_slug': 'base', 'grade_slug': 'grade', 'school_slug': 'school'}, url_name='community_recent', app_name='None', namespace='')
"""

# and also:

"""
>>> resolve('/community/base/school/grade/class')

ResolverMatch(func=<function this_community at 0x10307a500>, args=(), kwargs={'class_slug': 'class', 'base_slug': 'base', 'grade_slug': 'grade', 'school_slug': 'school'}, url_name='community-view', app_name='None', namespace='')
"""

# So that if we only want news for the school, 'recent' is taken
# up as a slug for the grade:

"""
>>> resolve('/community/base/school/recent')

ResolverMatch(func=<function show_recent at 0x1031a50c8>, args=(), kwargs={'class_slug': None, 'base_slug': 'base', 'grade_slug': None, 'school_slug': 'school'}, url_name='community-recent', app_name='None', namespace='')

"""

