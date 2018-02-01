## Regular Expressions ##
# In computing, a regular expression, also referred to as
# "regex" or "regexp", provides a concise and flexible
# means for matching strings of text, such as particular
# characters, words, or patterns of characters. 

## Cheat Sheet ##
# ^ 		Matches the beginning of a line
# $ 		Matches the end of the line
# . 		Matches any character
# \s 		Matches whitespace
# \S 		Matches any non-whitespace character
# * 		Repeats a character zero or more times
# *? 		Repeats a character zero or more times (non-greedy)
# + 		Repeats a chracter one or more times
# +? 		Repeats a character one or more times (non-greedy)
# ?         Repeats a character 0 or one time
# [aeiou] 	Matches a single character in the listed set
# [^XYZ] 	Matches a single character not in the listed set
# [a-z0-9] 	The set of characters can include a range
# ( 		Indicates where string extraction is to start
# ) 		Indicates where string extraction is to end
# \d        Matches any digit
# \b        Matches a word boundary

# load regex module
import re

# use search to check if match exists
# match_exists = re.search('regex', string)
old_macdonald = "eieio"
just_vowels = re.search('^[aeiou]+$', old_macdonald)
print just_vowels

farmer_in_the_dell = "hi ho the dary-o the farmer in the dell"
just_vowels = re.search('^[aeiou]+$', farmer_in_the_dell)
print just_vowels

# use find all to extract matches
# use parenthesis to tell what you want to capture
ants_go_marching = "The ants go marching 1 by 1 hurrah, hurrah"
all_numbers = re.findall('([0-9]+)', ants_go_marching)
print all_numbers

# you don't have to capture the whole match
old_macdonald2 = "and on his farm he had an elk eieio"
#what does the question mark do in a regex?
macdonalds_animals = re.findall('he had an? ([A-Za-z]+)', old_macdonald2)
print macdonalds_animals

# Now lets play with regexs
# http://www.regexr.com/
