#I have a list of strings in a text file (`mylist.txt`). I want to search for these strings in a tsv file (`somestuff.tsv`) and make a new file that contains only the lines in which the strings appear. Some strings in the text file will not appear in the tsv file.

#see https://gist.github.com/MartinPaulEve/c0610fa89da4df4d546a

#!/usr/bin/env python
output = []

# use a "with" block to automatically close I/O streams
with open('mylist.txt') as word_list:

    # read the contents of mylist.txt into the words list using list comprehension
    words = [word.strip().lower() for word in word_list]

with open('stuff.tsv') as tsv:
    # read the contents of stuff.tsv into the line list using list comprehension
    lines = [line for line in tsv]

# iterate over the lines
for line in lines:

    # iterate over the word list
    for word in words:

        # if we find one of the words in the line, then add it to the output list
        if word in line.lower():

            # if the TSV line doesn't end with a newline character, insert one
            if line.endswith('\n'):
                output.append(line)
            else:
                output.append('{0}\n'.format(line))

            # write some debug output to the console
            print('Found line {0} that matched word {1}'.format(line, word))

# open output.tsv using a with block with write permissions
with open('output.tsv', 'w') as output_file:

    # write the output list to the file
    output_file.writelines(output)

#Before Martin intervened, I was stuck figuring out how to query 'words' against 'ids[1]'. And then how to make a new file containing all the lists.