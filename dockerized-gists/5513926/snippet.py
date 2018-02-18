import requests

def doi2bib(doi):
  """
  Return a bibTeX string of metadata for a given DOI.
  """

  url = "https://doi.org/" + doi

  headers = {"accept": "application/x-bibtex"}
  r = requests.get(url, headers = headers)

  return r.text
