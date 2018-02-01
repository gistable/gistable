import os, sys

markdown_name = sys.argv[1]
name = markdown_name.split(".")[0]
latex_name = name + ".tex"

os.system("pandoc -f markdown -t latex %s -o %s" % (markdown_name, latex_name))

with open(latex_name, "r") as latex_file:
        latex_content = latex_file.read()

latex_content = """
                \documentclass[a4paper,12pt,parskip=full]{scrartcl}
                \usepackage{setspace}
                \doublespacing
                \\begin{document}
                %s
                \end{document}
                """ % (latex_content)

with open(latex_name, "w") as latex_file:
        latex_file.write(latex_content)

os.system("pdflatex %s" % (latex_name))