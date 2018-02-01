import django
from django.utils.translation import ugettext_lazy as _
from debug_toolbar.panels import DebugPanel
from haystack.backends import queries

class HaystackDebugPanel(DebugPanel):
    """
    Panel that displays the Haystack queries.
    """
    name = 'Haystack'
    has_content = True
    
    def nav_title(self):
        return _('Haystack queries')

    def nav_subtitle(self):
        return "%s queries" % len(queries)

    def url(self):
        return ''

    def title(self):
        return 'Haystack Queries'

    def content(self):
        return "".join(["<p>%s<br><br></p>" % q for q in queries])