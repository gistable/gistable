import console
import clipboard
import webbrowser

def main():
	text = clipboard.get()
	noNewlines = text.replace('\n',' ')
	array = noNewlines.split(' ')
	ABString = finalStringFromArray(array)
	clipboard.set(ABString)
	webbrowser.open('alienblue://')


def finalStringFromArray(array):
	removeX = shouldRemoveX(array)
	finalString = ''
	i = 0
	for  i in range(0,len(array)):
		if array[i] != None:
			if array[i][:3] == 'add':
				break
			if array[i][:3] == '/r/':
				if removeX:
					finalString = finalString + array[i][3:-1]
				else:
					finalString = finalString + array[i][3:]
				finalString = finalString + "+"
	finalString = finalString[:-1]
	return finalString

def shouldRemoveX(array):
	numX = 0
	numReddits = 0
	for  i in range(0,len(array)):
		if array[i] != None:
			if array[i][:3] == 'add':
				break
			if array[i][:3] == '/r/':
				numReddits +=1
				if array[i][-1:] ==  'x':
					numX += 1
	return numReddits == numX

main()