words = [
	["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"],
	["", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "ninteen"],
	["", "ten", "twenty", "thirty", "fourty", "fifty", "sixty", "seventy", "eighty", "ninty"]
]

out = ""

def triplets(num):
	msg = ""
	if num:
		d1 = num % 10
		d2 = (num//10)%10
		d3 = (num//100)%10
		msg += words[0][d3]
		if d3:
			msg += " hundred "
		if d2 == 1:
			msg += words[1][d1]
		else:
			if d2:
				msg += words[2][d2] + " " 
			msg += words[0][d1]
	return msg

x = int(input(" The number please : "))

p5 = (x//10**12)%1000
p4 = (x//10**9)%1000
p3 = (x//10**6)%1000
p2 = (x//10**3)%1000
p1 = x%1000

out += triplets(p5)
if p5:
	out += " trillion, "
out += triplets(p4)
if p4:
	out += " billion, "
out += triplets(p3)
if p3:
	out += " million, "
out += triplets(p2)
if p2:
	out += " thousand, "
out += triplets(p1)

print(out)

