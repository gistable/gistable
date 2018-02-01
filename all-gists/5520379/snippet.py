from ghost import Ghost
from functools import wraps

def fix_redirect(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        page, resources = func(self, *args, **kwargs)
        if resources and 300 <= resources[0].http_status <= 399:
            nextUrl = resources[0].headers['Location']
            page, resources = self.open(nextUrl)
        return page, resources
    return wrapper

class GhostRedirectFix(Ghost):
    @fix_redirect
    def open(self, *args, **kwargs):
        return Ghost.open(self, *args, **kwargs)

    @fix_redirect
    def click(self, *args, **kwargs):
        return Ghost.click(self, *args, **kwargs)

    @fix_redirect
    def evaluate(self, *args, **kwargs):
        return Ghost.evaluate(self, *args, **kwargs)

    @fix_redirect
    def fill(self, *args, **kwargs):
        return Ghost.fill(self, *args, **kwargs)

    @fix_redirect
    def fire_on(self, *args, **kwargs):
        return Ghost.fire_on(self, *args, **kwargs)

    @fix_redirect
    def set_field_value(self, *args, **kwargs):
        return Ghost.set_field_value(self, *args, **kwargs)

    def find_elements_by_tag_name(self, tag):
        return self.find_element_by_css_selector(tag)

browser = GhostRedirectFix()