import re

def url_matcher():
    """
    See: http://daringfireball.net/2010/07/improved_regex_for_matching_urls
    """
    return re.compile(
        ur"""(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)"""
        ur"""(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+"""
        ur"""(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()"""
        ur"""\[\]{};:'".,<>?\u00AB\u00BB\u201C\u201D\u2018\u2019]))"""
    )
