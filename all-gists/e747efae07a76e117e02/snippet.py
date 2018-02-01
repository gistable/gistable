def OCR(freq, prescaler):
	return (16000000 / (prescaler * freq)) - 1

def HZ(ocr, prescaler):
	return (16000000 / (prescaler * (ocr+1)))
	
def checkBit(data, bit):
	return bool(data & (1<<bit))
	
def checkTimerValid(li):
	for li1 in li:
		for li2 in li:
			if type(li2[1]) is not str:
				return True
	
def twoDec(val):
	return "{0:.2f}".format(val)
	
def stringifyTop(timer, freq, actual):
	return "\n\
void setup()\n\
{\n\
  cli();\n\
  \n\
//set timer"+str(timer)+" interrupt at "+str(freq)+"Hz ("+twoDec(actual)+")\n\
  TCCR"+str(timer)+"A = 0;\n\
  TCCR"+str(timer)+"B = 0;\n\
  TCNT"+str(timer)+" = 0;\n\
  \n"

def stringifyBottom(timer):
	return "\n\
  sei();\n\
}\n\
\n\
ISR(TIMER"+str(timer)+"_COMPA_vect){\n\
  //Interrupt Code Here\n\
}"

def stringifyOCR(timer, n):
	return "  OCR"+ str(timer)+"A = "+str(n)+";\n"

def stringifyPrescaler(timer, index):
	line = "  TCCR"+str(timer)+"B |="
	for bit in [2,1,0]:
		if checkBit(index+1, bit):
			line+=" (1 << CS"+str(timer)+str(bit)+") |"
	return line[:-2]+";\n"

def stringifyCTC(timer):
	return "  TCCR"+str(timer)+("A" if timer!=1 else "B")+" |= (1 << WGM"+str(timer)+("1" if timer!=1 else "2")+");\n"

def stringifyEnable(timer):
	return "  TIMSK"+str(timer)+" |= (1 << OCIE"+str(timer)+"A);\n"

#main
prescalers = [1,8,64,256,1024]
prescalers2 = [1,8,32,64]	
output = [[],[],[]]#timer0,timer1,timer2 inner [prescaler, OCR]
desired_freq = int(input("Desired Frequency? (Hz): "))

for timer in range(3):
	maxOCR = 255
	if timer == 1:
		maxOCR = 65535
	for prescaler in (prescalers if timer!=2 else prescalers2):
		ocr = OCR(desired_freq, prescaler)
		acc = 0;
		if ocr > maxOCR or ocr < 1:
			acc = ""
			ocr = ""
		else:
			acc = twoDec(100-abs(ocr-int(round(ocr)))/ocr*100)
			ocr = int(round(ocr))
		output[timer].append([prescaler, ocr, acc])

head = ["index", "prescaler", "OCR", "accuracy"]
row_format = "{!s:>6}{!s:>11}{!s:>7}{!s:>11}"
for i in range(len(output)):
	timer = output[i]
	print()
	print(row_format.format("","timer"+str(i),"",""))
	print(row_format.format(*head))
	for i in range(len(timer)):
		print(row_format.format(i,*timer[i]))
		
timer = int(input("Choose a timer (0,1,2): "))
while not (timer >= 0 and timer <= 2 and checkTimerValid(output[timer])):
	timer = int(input("Not an option. Choose a timer (0,1,2): "))

pscale = int(input("Choose a prescaler index: "))
while not (pscale >= 0 and pscale <= (4 if timer!=2 else 3) and type(output[timer][pscale][1]) is not str):
	pscale = int(input("Not an option. Choose a prescaler index: "))

	
print(stringifyTop(timer,desired_freq,HZ(output[timer][pscale][1], output[timer][pscale][0]))+\
stringifyOCR(timer, output[timer][pscale][1])+\
stringifyCTC(timer)+\
stringifyPrescaler(timer,pscale)+\
stringifyEnable(timer)+\
stringifyBottom(timer))
