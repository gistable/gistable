def neither(subject, *objects, compare=lambda s,o: s == o):
	for object in objects:
		if subject == object:
			return False
	return True