'''
Mathew Del Signore
AMS210 oil problem(1.2)
checks values from 1 to 50 to see which solve a group
of equations within 30 of the desired answers
'''

#x values for formula
x1 = 0
x2 = 0
x3 = 0

for k in range(1,50):
	x1=k
	for i in range(1,50):
		x2=i
		for j in range(1,50):
			x3=j
			ans1=(6*x1)+(3*x2)+(2*x3)
			if abs(ans1-280)<30:
				ans2=(4*x1)+(6*x2)+(3*x3)
				if abs(ans2-350)<30:
					ans3=(3*x1)+(2*x2)+(6*x3)
					if abs(ans3-350)<30:
						print("x1: %i  x2: %i  x3: %i\n"%(x1,x2,x3))
					
				