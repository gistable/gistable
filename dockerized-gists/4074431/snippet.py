def shareSingleNote(authToken, noteStore, userStore, noteGuid, shardId=None):
	"""
	Share a single note and return the public URL for the note
	"""
	if not shardId:
		shardId = getUserShardId(authToken, userStore)
		if not shardId:
			raise SystemExit

	try:
		shareKey = noteStore.shareNote(authToken, noteGuid)
	except (EDAMNotFoundException, EDAMSystemException, EDAMUserException), e:
		print "Error sharing note:"
		print type(e), e
		return None

	return "%s/shard/%s/sh/%s/%s" % \
		(EN_URL, shardId, noteGuid, shareKey)