f = open('user.yaml')

dataMap = yaml.load(f)

f.close()
print ""
print "=-----------="
print "dataMap is a ", type(dataMap), dataMap
print "=-----------="
print "main items are", type(dataMap['main']), dataMap['main']
print "=-----------="
print "main is a list, the first item is a dictionary", type(dataMap['main'][0]), dataMap['main'][0]
print "=-----------="
print "main[0] is a dict, the first item is", dataMap['main'][0]['users'][0]


"""
Sample YAML File:

- users:
    - joe
    - mike
    - sally

  - path:
    - /Users/me/files/
    - text.files

  - search_phrases:
    - Invalid users
    - Failed password

"""