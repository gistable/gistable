def remdup(l, dup=None):
	# If has zero or one elements, there are no duplicates.
	if len(l) < 2:
		return l

	# If there's a duplicate to remove, remove it and recurse until ValueError
	# is raised, which means there are none left to remove. Since lists are
	# mutable, we don't have to capture this.
	if dup is not None:
		try:
			l.remove(dup)
			remdup(l, dup)
		except ValueError:
			pass

	# No more duplicates to remove? Then recurse, removing duplicates of the
	# current head!
	return [l[0]] + remdup(l[1:], l[0])
