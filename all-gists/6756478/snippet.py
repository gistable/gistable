class InvalidStringHandler(object):
    """Custom handler for invalid string in templates."""
    
    def __call__(self):
        """Force crashes in {{ foo|sth }}, without breaking __str__."""
        import ipdb; ipdb.set_trace()
        raise ValueError()

    def __nonzero__(self):
        """So that '{% if foo %}' doesn't break."""      
        return False                                                                       
        
    def __contains__(self, key):
        """There is a test for '%s' in TEMPLATE_STRING_IF_INVALID."""
        return key == '%s'

    def __mod__(self, var):        
        """Handles TEMPLATE_STRING_IF_INVALID % var"""
        raise ValueError("Undefined template variable %r" % var)
            
TEMPLATE_STRING_IF_INVALID = InvalidStringHandler()                                                                                
                
