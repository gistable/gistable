import csv
import os
import sys

from os.path import isfile
from datetime import date, timedelta
from subprocess import call, check_output

# Script expects that each project is in a folder with the same name in the working directory
PROJECTS = ['my-project', 'another-project']

# Configure to group languages, those not listed will be left as is
LANG_GROUPS = {
  'HTML/CSS': ['HTML', 'HAML', 'CSS', 'Ruby HTML', 'SASS'],
  'JS': ['Javascript', 'CoffeeScript'],
  'Other': ['XML', 'IDL', 'DOS Batch', 'Bourne Again Shell', 'Bourne Shell', 'ASP.Net', 'make', 'YAML', 'SQL']
}

# Git functions
def checkout_at(project, date):
  rev = revision_for(project, date)
  if not rev: return False
  print "Checking out %s from %s for %s" % (rev, date, project)
  checkout_rev(project, rev)
  return True

def revision_for(project, date):
  try:
    format = ['-n1', '--date-order', '--oneline', '--no-abbrev-commit']
    return check_output(git_for(project) + ['log', 'origin', '--before="%s"' % (date.isoformat())] + format).split()[0]
  except:
    None

def checkout_rev(project, revision):
  call(git_for(project) + ['checkout', '--detach', '--force', revision], stdout=None)

def git_for(project):
  return ['git', '--git-dir=%s/.git' % (project), '--work-tree=%s' % (project)]

# Cloc functions
def call_cloc(projects, outfile):
  definitions = ['--force-lang-def=definitions.txt'] if isfile('definitions.txt') else []
  call(['cloc'] + projects + definitions + ['--csv', '--quiet', '--out=%s' % (outfile)])

def parse_cloc(file):
  lines_by_language = {}
  with open(file, 'r') as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
      files, language, blank, comment, code = row
      if int(code) > 0: lines_by_language[language] = int(code)
  return lines_by_language

def cloc(projects, fname):
  fname = str(fname)
  call_cloc(projects, fname)
  lines_by_language = parse_cloc(fname)
  os.remove(fname)
  return lines_by_language

# Date functions
def weeks(start, upto):
  return [date.fromordinal(d) for d in range(start.toordinal(), upto.toordinal(), 7)]

# Data handling
def group(lines_by_language_by_date, lang_groups={}):
  grouped = dict()
  languages = set()

  lang_to_group = {}
  for k,vs in lang_groups.iteritems():
    for v in vs: lang_to_group[v] = k

  for d, lines_by_language in lines_by_language_by_date.iteritems():
    grouped[d] = lines_by_language = dict(lines_by_language)
    for lang, lines in lines_by_language.items():
      if lang in lang_to_group:
        group = lang_to_group[lang]
        if group != lang:
          lines_by_language[group] = lines_by_language.get(group, 0) + lines
          del lines_by_language[lang]
    languages = languages.union(lines_by_language.keys())

  return grouped, list(languages)

def write_csv(lines_by_language_by_date, languages, outfile=sys.stdout):
  writer = csv.writer(outfile)
  writer.writerow(['Date'] + languages)
  for d, lines_by_language in lines_by_language_by_date.iteritems():
    row = [d] + [lines_by_language.get(lang, 0) for lang in languages]
    writer.writerow(row)

# Main body
def main(projects, start, upto):
  lines_by_language_by_date = {} # date => lang => lines

  for d in weeks(start, upto):
    ps = [project for project in projects if checkout_at(project, d)]
    data = cloc(ps, d.toordinal())
    lines_by_language_by_date[d] = data

  groups,langs = group(lines_by_language_by_date, LANG_GROUPS)
  with open('stats.csv', 'w') as f: write_csv(groups, langs, f)
  print "Successfully wrote output to stats.csv"

# Run!
main(PROJECTS, date(2013,7,1), date(2013,12,31))
