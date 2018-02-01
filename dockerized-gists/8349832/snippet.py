import mimetypes

def is_txt_file(file):
    """Test if the file is a txt file."""

    mime = mimetypes.guess_type(file)
    if mime[0] == 'text\plan':
        return True