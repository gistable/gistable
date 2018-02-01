import os
rfiles = os.listdir('.')
rc = []
for f in rfiles:
    if '.txt' in f: 
    # The recipes come in 3 txt files consisting of 1 recipe per line, the 
    # cuisine of the recipe as the first entry in the line, and all subsequent ingredient
    # entries separated by a tab
        infile = open(f, 'r')
        rc.append(infile.read())
        infile.close()
all_rs = '\n'.join(rc)
import re
line_pat = re.compile('[A-Za-z]+\t.+\n')
recipe_lines = line_pat.findall(all_rs)
new_recipe_lines = []
cuisine_lines = []
for n,r in enumerate(recipe_lines):
    # First we find the cuisine of the recipe
    cuisine = r[:r.find('\t')]
    # Then we append the ingredients withou the cuisine
    new_recipe_lines.append(recipe_lines[n].replace(cuisine, ''))
    # I saved the cuisines to a different list in case I want to do some 
    # cuisine analysis later
    cuisine_lines.append(cuisine + '\n')

outfile1 = open('recipes combined.tsv', 'wb')
outfile1.write(''.join(new_recipe_lines))
outfile1.close()

outfile2 = open('cuisines.csv', 'wb')
outfile2.write(''.join(cuisine_lines))
outfile2.close()