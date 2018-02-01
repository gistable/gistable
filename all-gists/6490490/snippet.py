import re
 
phyel=open('declaration.txt','r')  #open the file
x = re.split('\W+', phyel.read().replace("'","")) 
lines = x

# to accommodate the "capture list" and allow it be dynamic in this environment
wrdset=set()
for wds in x:
    word = wds.lower()
    wrdset.add(wds)

lengthct = [0]*16 

#subdivides lines in words and counts words if 
for line in lines:
    words = line.split()     
    for word in words:
        lword=word.lower().strip()
        if lword ==  word.lower().strip():
            lengthct[len(word)]+=1

print("Length Count\n")
for i, ct in enumerate(lengthct):
    if ct:
        # nicely formated output:
        print("{:>3d}:{:>2d}".format(i,ct))
        
print("\n") 

x = 0 # keep track of list position
r=500
while r< 501:  
    print(r,"| ",end='')
    for items in lengthct:
        if r > int(items):    	
            print("  ",end=' ')
            x+=1
        elif r <= int(items):
            print(" *",end=' ')
            x+=1
        if x == len(lengthct):
            r-=20
            x=0
            print("\n") 
    if r<-1:		
        print("-"*30)			
        print("  ",end=" ")
        for items in lengthct:
            items
            print(x,end=" ")
            x+=1
        break