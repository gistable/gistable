import clipboard

text = raw_input("Input link text: ")
link = '['
link = link + text
link = link + ']'
link = link + '('
link = link + clipboard.get()
link = link + ')'
clipboard.set(link)
print "\n\n Markdown link set to clipboard"
    
