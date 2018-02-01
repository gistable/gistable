# generate possible combinations of a word, sort them and find position
# of the input word in the sorted list.

word = raw_input("Enter a string")

output = list() # will have word combinations

# move a char to the start of word and them arrange others after it
gen_comb = lambda word, index: word[index]+ word[0:index] + word[index+1:]

index = 0 # keeps track of current location in the word
for c in word:
    output.append(gen_comb(word, index)) # append combinations to output
    index += 1

output.sort() # sort alphabetically

# find the position of input word in the sorted list
for item in output:
    if item == word:
        print "The word rank is: %d" % (output.index(item) + 1) # count starts from 0, we start ranking from 1
