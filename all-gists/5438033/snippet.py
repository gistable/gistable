import re
import random


CURLY_RE = re.compile( "\{(.*?)\}" )

def spam( filename ):
    
    
    file = open(filename, "r")
    all_templates = file.read().split( "|\n")
    
    N = len( all_templates )
    
    #randomly choose a spam template
    spammy_template = all_templates[ random.randint(0, N-1) ]
    
    
    formatted_spam = re.sub( CURLY_RE, "%s", spammy_template )
    
    choices = []
    for _template in re.findall( CURLY_RE, spammy_template):
        _choices = _template.split("|")
        choices.append( _choices[ random.randint( 0, len(_choices)-1 ) ] )
    
    return formatted_spam%tuple(choices )
        
    
    
    