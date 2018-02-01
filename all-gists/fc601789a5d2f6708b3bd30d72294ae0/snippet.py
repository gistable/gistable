def mimimi(frase):
  """
  Função que mimimiza frases
  >>> mimimi('Por que você não tá estudando pra sua prova de amanhã?')
  'Pir qii vici nii ti istidindi pri sii privi di iminhi?'
  """
  n = ('ã', 'a', 'e', 'o', 'u', 'á', 'é', 'ê', 'í', 'ó')
  for letra in n:
    frase = frase.replace(letra, 'i')
  return frase


def mememe(frase):
  """
  Função que retorna um link pra uma imagem mememe do mimimi
  """
  url_template = "https://memegen.link/custom/{original}/{mimimi}.jpg?alt=https://i.imgur.com/UvvvAJP.jpg&font=impact"
  mimimizado = mimimi(frase)
  url = url_template.format(original=frase, mimimi=mimimizado)
  return url
  