import csv
import requests
import bs4 as bs

def wormbase_url(gene_id):
    """
    Return the correct REST API URL, given the gene ID.
    """
    url = "http://www.wormbase.org/rest/widget/cds/" + gene_id + "/sequences"
    return url

def file_lines(file_name):
    """
    Count the number of lines in a file.
    """
    f = open(file_name)
    return len(f.readlines())

def parse_unspliced(html):
    """
    Parse the raw HTML file for the unspliced gene data.
    """
    soup = bs.BeautifulSoup(html)
    content = soup.find(id="content")
    return content.string.replace('\n', '')

def get_sequences(csv_name, output_name, error_name):
    """
    From the CSV file, get the gene IDs and access the Wormbase REST API.
    Write successful requests with the unspliced sequences to an output file.
    Log the failed gene IDs to a separate file.

    Keyword arguments:
    csv_name -- the name of the CSV file to read from
    output_name -- the name of the file with the unspliced gene data
    error_name -- the name of the file that logs the unsuccessful requests
    """
    num_genes = str(file_lines(csv_name))
    out_file = open(output_name, "w")
    err_file = open(error_name, "w")

    gene_reader = csv.reader(open(csv_name, 'rb'))
    gene_count = 0
    failed_genes = []

    for row in gene_reader:
        
        gene_id = row[0]
        gene_count += 1
        gene_data = requests.get(wormbase_url(gene_id))
        
        if (gene_data.status_code == 200):
            unspliced_gene = parse_unspliced(gene_data.text)
            out_file.write(unspliced_gene + "\n")
            print gene_id + ": SUCCESS (" + str(gene_count) + "/" + \
                  str(num_genes) + ")"
        else:
            err_file.write(gene_id + "\n")
            print gene_id + ": ERROR " + str(gene_data.status_code) + \
                  " (" + str(gene_count) + "/" + str(num_genes) + ")"

def main():
    get_sequences("4699genes.csv", "4699genes.out", "4699genes.err")

if __name__ == "__main__":
    main()