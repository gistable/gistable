#統計字串的英文字母
a="hello kitty"
sumstr = {}
for i in a:
	sumstr[i] = 0 
	for j in a:
		if(i==j):
			sumstr[i]+=1 		
print(sumstr)
