import json

data = json.loads(geojson)
all_linestrings = []
new_linestring = []
inserted = 0

for elements in data["features"]:
	if elements["geometry"]["type"] == "LineString":
		ls = elements["geometry"]["coordinates"]
		all_linestrings.append(ls)


while inserted < len(all_linestrings):
	for linestring in all_linestrings:
		if new_linestring == []:
			new_linestring.extend(linestring)
		elif linestring[0] in new_linestring: # anfang des teilstücks
			pos = new_linestring.index(linestring[0])
			if pos == 0: # anfang des teilstücks = anfang der gesamtlinie
				new_linestring = linestring[::-1] + new_linestring
				inserted += 1
			elif pos == len(new_linestring)-1: # anfang des teilstücks ende der gesamtlinie
				new_linestring = new_linestring + linestring
				inserted += 1
		elif linestring[-1] in new_linestring:
			pos = new_linestring.index(linestring[-1])
			if pos == 0:
				new_linestring = linestring + new_linestring
				inserted += 1
			elif pos == len(new_linestring)-1:
				new_linestring = new_linestring + linestring[::-1]
				inserted += 1

print(new_linestring)