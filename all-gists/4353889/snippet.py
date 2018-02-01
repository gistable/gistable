import argparse, sys
from lxml import etree

class PMDTransformer(object):
  def __init__(self):
    self.etree = None
    self.args = None
    self.violations = None

  def parse(self):
    self.etree = etree.parse(self.args.infile).getroot()

  def get_issues(self):
    self.violations = etree.XML('<div id="violations" class="span8"></div>')
    for x in range(1,6):
      r = self.etree.xpath('/pmd/file/violation[@priority="{0:d}"]'.format(x))
      for violation in r:
        self.do_one(violation)

  def do_one(self, violation):
    rule = violation.get('rule')
    fn = violation.getparent().get('name')
    begin = violation.get('beginline')
    end = violation.get('endline')
    text = violation.text.strip()
    node = etree.XML("""<div class="finding">
      <h4>{1:s}</h4><br />
      <strong>Severity: {0:s}</strong><br />
      <em>{2:s}</em>:{3:s}-{4:s}<br />
      {5:s}<br />
      </div>""".format(
                      violation.get('priority'),
                      rule,
                      fn,
                      begin,
                      end,
                      text))
    pre = etree.XML('<pre class="prettyprint linenums:{0:s} lang-java" style="padding-left:20px"></pre>'.format(begin))
    try:
      infile = open(fn, 'r')
      lines = infile.readlines()
      pre.text = ''.join(lines[int(begin) - 1:int(end)])
    except Exception, e:
      pre.text = 'NO EVIDENCE AVAILABLE'
      print e.message
    node.append(pre)
    self.violations.append(node)

  def print_html(self):
    html = etree.XML('''<!DOCTYPE html>
      <html>
      <head>
      <title>Violations</title>
      <link rel="stylesheet" href="bootstrap.min.css" media="screen"></link>
      <link rel="stylesheet" href="bootstrap-responsive.min.css" media="screen"></link>
      <link rel="stylesheet" href="report.css" media="screen"></link>
      <link rel="stylesheet" href="prettify.css"></link>
      <script language="javascript" src="prettify.js"> </script>
      </head>
      </html>''')
    body = etree.XML('<body onload="prettyPrint()"><div class="row"><div class="span2"></div></div></body>')
    body.append(self.violations)
    body.append(etree.XML('<div class="span2"></div>'))
    html.append(body)
    self.args.outfile.write(etree.tostring(html, pretty_print=True, doctype="<!DOCTYPE html>"))

  def main(self):
    parser = argparse.ArgumentParser(description='Transform PMD output to HTML')
    parser.add_argument('-i', '--infile', nargs='?', type=argparse.FileType('r'),
                        default=sys.stdin)
    parser.add_argument('-o', '--outfile', nargs='?', type=argparse.FileType('w'),
                        default=sys.stdout)
    self.args = parser.parse_args()
    self.parse()
    self.get_issues()
    self.print_html()

if __name__ == '__main__':
  PMDTransformer().main()
