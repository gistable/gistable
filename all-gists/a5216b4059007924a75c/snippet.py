# Notes:
# Python 3 assumed, but shouldn't be hard to backport to Python 2
# Cobbled together from two slightly different implementations, sorry for any inconsistencies.

# This creates two models, NavigationMenu, and NavigationMenuItem. A site can have many NavigationMenus, which are referenced from
# the template by location. E.g., 'footer', 'left_nav'. You can also create single-item lists for special purpose links/buttons,
# such a privacy_policy or homepage_cta. This helps to reduce hard coding in templates.

# NavigationMenuItem mixes in some different link types (Page, Document, URL) and presents them in a consistent way. It provides
# the ability to override the title of the referenced object.

# In models.py:
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
    def url(self):
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
        
class NavigationMenuItem(Orderable, LinkFields):
    menu = ParentalKey(to='core.NavigationMenu', related_name='menu_items')
    menu_title = models.CharField(max_length=255, blank=True, null=True,
                                  help_text="Optional link title in this menu (defaults to page title if one exists)")

    @property
    def menu_item_title(self):
        if self.menu_title:
            return self.menu_title
        if self.link_page:
            return self.link_page.title
        elif self.link_document:
            return self.link_document.title
        else:
            return self.link_external

    def __str__(self):
        return self.menu_item_title

    panels = [FieldPanel('menu_title')] + LinkFields.panels


class NavigationMenuManager(models.Manager):
    def get_by_natural_key(self, menu_location):
        return self.get(menu_location=menu_location)


@register_snippet
class NavigationMenu(ClusterableModel):
    objects = NavigationMenuManager()
    menu_location = models.CharField(null=False, max_length=255, help_text="Template name (do not change)", unique=True)
    menu_name = models.CharField(null=True, blank=True, max_length=255)

    def __str__(self):
        name = self.menu_name
        if not name:
            name = "Unnamed"

        return "{name} ({location})".format(name=name, location=self.menu_location)

NavigationMenu.panels = [
    FieldPanel('menu_name'),
    InlinePanel('menu_items', label="Linked Pages"),
    FieldPanel('menu_location')
]

# In templatetags/my_tags.py:

@register.assignment_tag(takes_context=False)
def load_navigation_menu(location):
    try:
        return NavigationMenu.objects.get_by_natural_key(location)
    except NavigationMenu.DoesNotExist:
        logger.critical("No such navigation menu %s", location)
        
        
# In some_template.html

{% load_navigation_menu 'footer' as footer_menu %}
<ul class="all-caps no-bullets">
    {% for menu_item in footer_menu.menu_items.all %}
    <li><a href="{{ menu_item.url }}">{{ menu_item }}</a></li>
{% endfor %}