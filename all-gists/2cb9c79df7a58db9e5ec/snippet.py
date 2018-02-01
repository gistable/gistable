import pdftableextract as pdf
import csv

pages = [str(i) for i in range(1, 7)]
cells = [pdf.process_page("./List_of_current_step_companies.pdf", p)
         for p in pages]

# fatten cells
cells = [item for sublist in cells for item in sublist]

# XXX: I'm not able to list the companies on page 6
company_names = [col[-1] for col in cells if col[0] is 1]
founders = [col[-1] for col in cells if col[0] is 2]
email_ids = [col[-1] for col in cells if col[0] is 3]

companies = zip(company_names, founders, email_ids)
list_file = open('list.md', 'w')
list_file.write("\n".join(company_names))
list_file.close()

with open("list.csv", "wb") as f:
    writer = csv.writer(f)
    writer.writerows(companies)
