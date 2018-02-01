data_uri = open("sample.png", "rb").read().encode("base64").replace("\n", "")
# HTML Image Element
img_tag = '<img alt="" src="data:image/png;base64,{0}">'.format(data_uri)
print img_tag
# CSS Background Image
css = 'background-image: url(data:image/png;base64,{0});'.format(data_uri)
print css