from plasTeX.TeX import TeX

# The following can be a problem if you are using revtex.
doc = TeX(file="filename.tex").parse()

refs = doc.getElementByTagName("cite")

cites = []

for ref in refs:
    cites += ref.attributes["bibkey"]

# Remove duplicate entries.
cites = list(set(cites))