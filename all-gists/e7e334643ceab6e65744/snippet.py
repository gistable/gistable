# Thanks to Ethan Jucovy
# http://www.coactivate.org/projects/ejucovy/blog/2014/05/10/wagtail-notes-managing-redirects-as-pages/

# This model comes from wagtaildemo

class LinkFields(models.Model):
    link_external = models.URLField("External link", blank=True)
    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+'
    )
    link_document = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        related_name='+'
    )

    @property
    def link(self):
        if self.link_page:
            return self.link_page.url
        elif self.link_document:
            return self.link_document.url
        else:
            return self.link_external

    panels = [
        FieldPanel('link_external'),
        PageChooserPanel('link_page'),
        DocumentChooserPanel('link_document'),
    ]

    class Meta:
        abstract = True

# This is the model you are looking for
# from wagtail.wagtailcore.models import Page

class PageAlias(Page, LinkFields):

    def serve(self, request):
        return redirect(self.link, permanent=False)

PageAlias.content_panels = [FieldPanel('title')] + LinkFields.panels
