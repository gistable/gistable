# instiki_to_mediawiki.py

from optparse import OptionParser
import os.path
import re
import cgi
import sys
import subprocess

category_regex = re.compile(r"(:)?category\s*:(.*)", re.IGNORECASE)
redirect_regex = re.compile(r"\[\[\!redirects\s+([^\]\s][^\]]*?)\s*\]\]", re.IGNORECASE)
toc_regex = re.compile(r"\=\s*Contents\s*\=\s*\n*\s*\*\s*table of contents", re.IGNORECASE)

def remove_tocs(contents):
  return toc_regex.sub("", contents)

def title_to_wiki_style(s):
  s = s.strip()
  if len(s) == 0:
    return s
  return s[0].upper() + s[1:]

def category_to_wiki_style(c):
  return "[[Category:%s]]" % cgi.escape(title_to_wiki_style(c))

def replace_category(match):
  return "\n".join(map(category_to_wiki_style, match.group(2).split(',')))

def replace_categories(input):
  return category_regex.sub(replace_category, input)

def get_redirects(contents):
  return map(lambda x: title_to_wiki_style(x.group(1)),
    redirect_regex.finditer(contents))

def remove_redirects(contents):
  return redirect_regex.sub("", contents)

def register_redirect(s, t, register):
  if s and t and s != t:
    if s not in register.keys():
      register[s] = t

def get_page_list(dir):
  return map(lambda x: dir + "/" + x.replace(".meta", ""),
    filter(lambda x: x.endswith(".meta"), os.listdir(dir)))

def get_page_title(p):
  meta = open(p + ".meta", 'r').read()
  r = re.compile(r"name\s*:(.*)", re.IGNORECASE)
  ms = r.findall(meta)
  if not ms:
    return
  else:
    return title_to_wiki_style(ms[-1])

def write_redirects_register(register, path):
  open(path, 'w').write("\n".join(
    ["%s -> %s" % (s, t) for s, t in register.items()]))

def convert_markdown_to_wiki_syntax(path):
  subprocess.call("C:/Ruby193/bin/ruby.exe "
    "C:/Users/khan/Documents/GitHub/maruku/bin/maruku "
    "--wiki --math-engine none %s" % path)

def main(input, output):
  redir_register = {}

  for p in get_page_list(input):
    x = open(p, 'r').read()

    x = remove_tocs(x)

    rs = get_redirects(x)
    x = remove_redirects(x)
    [register_redirect(r, get_page_title(p), redir_register) for r in rs]

    x = replace_categories(x)

    path = output + "/" + os.path.basename(p)
    open(path, 'w').write(x)

    convert_markdown_to_wiki_syntax(path)

  write_redirects_register(redir_register, "redirects.txt")

if __name__ == "__main__":
  parser = OptionParser("usage: %prog -i INPUT -o OUTPUT")
  parser.add_option("-i", "--input-dir", dest="input",
    help="A directory containing files exported from an Instiki installation, "
         "to be converted to MediaWiki format.")
  parser.add_option("-o", "--output-dir", dest="output",
    help="A directory to be populated with MediaWiki format files.")

  (options, args) = parser.parse_args()
  if not options.input:
    parser.error("missing input directory")
  elif not os.path.isdir(options.input):
    parser.error("input directory is not a directory")
  if not options.output:
    parser.error("missing output folder")
  elif not os.path.isdir(options.output):
    parser.error("output directory is not a directory")

  main(options.input, options.output)