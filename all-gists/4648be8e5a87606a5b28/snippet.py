#While this particular version takes files of the text on my followers and following pages, 
#it can be easily modified to check a past list of followers against a more recent list - 
#just replace following.txt with the "past followers" file and followers.txt with "present followers". 

#encoding may be 'utf-8' depending on the type of files you are using


with open('following.txt', 'r', encoding = 'latin-1') as following_file:
    with open('followers.txt', 'r', encoding = 'latin-1') as followers_file:
        discrepancy = set(following_file).difference(followers_file)

discrepancy.discard('\n')

with open('difference.txt', 'w', encoding = 'utf-8') as difference:
    for line in discrepancy:
        difference.write(line)
