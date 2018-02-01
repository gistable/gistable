# put this in your_app/models.py
def suite():
    """Django test discovery."""
    import nose
    import unittest
    path = os.path.join(os.path.dirname(__file__), 'tests')
    suite = unittest.TestSuite()
    suite.addTests(nose.loader.TestLoader().loadTestsFromDir(path))
    return suite