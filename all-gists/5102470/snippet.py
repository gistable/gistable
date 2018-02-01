import sys
import subprocess
import tempfile
import urllib

text = sys.stdin.read()

chart_url_template = ('http://chart.apis.google.com/chart?'
                      'cht=qr&chs=300x300&chl={data}&chld=H|0')
chart_url = chart_url_template.format(data=urllib.quote(text))

with tempfile.NamedTemporaryFile(mode='w', suffix='.png') as f:
    subprocess.check_call(['curl', '-L', chart_url],
                          stdout=f, stderr=sys.stderr)
    subprocess.check_call(['qlmanage', '-p', f.name])