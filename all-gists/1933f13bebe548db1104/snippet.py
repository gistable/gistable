import requests
import base64

@qgsfunction(args='auto', group='Custom')
def show_camera(feed, feature, parent):
	svg = """
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg>
  <g>
	<image xlink:href="data:image/jpeg;base64,{0}" height="256" width="320" />
  </g>
</svg>
"""
	data = requests.get(feed, stream=True).content
	name = feed[-16:]
	b64response = base64.b64encode(data)
	newsvg = svg.format(b64response).replace('\n','')
	path = r"C:\temp\camera\{0}.svg".format(name)
	with open(path, 'w') as f:
		f.write(newsvg)
	return path.replace("\\", "/")
