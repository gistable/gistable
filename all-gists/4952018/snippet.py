class CustomFormatter(logging.Formatter):
    def formatException(self, ei):
        """Format and return the exception information as a string.

        This adds helpful advice to the end of the traceback.
        """
        import traceback
        sio = StringIO.StringIO()
        traceback.print_exception(ei[0], ei[1], ei[2], file=sio)
        return sio.getvalue() + "... Don't panic!"
