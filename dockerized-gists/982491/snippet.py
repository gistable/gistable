#see the description at http://kochi-coders.com/?p=40
#!/usr/bin/env python
import cgi
import cgitb
cgitb.enable()
form=cgi.FieldStorage()

from math import pi, e, sin, cos ,atan,ceil,floor

#for creating chart from google chart api.
from graphy import bar_chart
from graphy.backends import google_chart_api

#for creating the chart
def makechart(mag):
	chart = google_chart_api.BarChart(mag)
	chart.left.min = 0
	chart.left.max=ceil(max(mag))
	chart.display.style.bar_thickness = 10
	chart.display.style = bar_chart.BarStyle()
	chart.display.style.grou_gap = 10
	chart.bottom.min = 0
	chart.bottom.max = len(mag)
	chart.bottom.labels = [z for z in range(len(mag))]
	chart.top.labels = mag

print "content-type: text/html;charset=utf-8"
print

xa = form["xa"].value
Fs = int(form["fs"].value)
n=int(form["no"].value)
N = int(form["length"].value)

x = [0.0] * max (n, N)
X=[]
mag=[]
angle=[]
print "<html><head>Output</head><body><p>Taking samples:"
for i in range (n):
	t = (i + 0.0) / Fs
	sample = eval (xa)
	print "<p>x(" + str(i) + ") =", sample
	x[i]=sample

print "<p>Taking", n, "point DFT:"
for k in range (n):
	X.append(sum ([x[m]*e**(-2j*pi*k*m/n) for m in range (n)]))
	print "<p>X(" + str(k) + ") =%s"%X[k]
	mag.append(abs(X[k]))
	if X[k].real !=0:
		angle.append((atan(X[k].imag/X[k].real)*180)/pi)
	else:
		angle.append("---") 
print '<br><br><br><br><br><font size="6">Values for magnitude plot:<br></font>%s<br>'%mag
mag=[ceil(y) for y in mag]

#here comes the  magnitude plot.
makechart(mag)

print '<p><p><p><p><p><p><p><p><br><br><br><h1>Magnitude plot</h1><img src="%s">'%chart.display.Url(400, 120)
print"<br>Values are approximated by taking ceil(magnitude)" 

print '<br><br><br><br><br><h1><p>Taking, %s, point DFT:</h1>'%str(N)
mag=[]
angle=[]
X=[]
for k in range (N):
	X.append(sum ([x[n]*e**(-2j*pi*k*n/N) for n in range (N)]))
	print "<p>X(" + str(k) + ") =%s"%X[k]
	mag.append(abs(X[k]))
	if X[k].real !=0:
		angle.append((atan(X[k].imag/X[k].real)*180)/pi)
	else:
		angle.append("---") 
print '<br><br><br><br><br><font size="6">Values for magnitude plot:<br></font>%s<br>'%mag
mag=[ceil(x) for x in mag]
  
makechart(mag)
print '<p><p><p><p><p><p><p><p><br><br><br><h1>Magnitude plot</h1><img src="%s">'%chart.display.Url(400, 120)
print"<br>Values are approximated by taking ceil(magnitude)" 
print'<p>Courtesy:&nbsp;&nbsp;&nbsp;<a href="http://twitter.com/vineethgn">Vineeth G Nair</a>&nbsp;&nbsp;&nbsp;</body></html>'