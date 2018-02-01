func _delete_data(path):
	var dir = Directory.new()
	var opened = dir.change_dir(path)
	if opened != OK:
		OS.alert("Error "+str(opened)+" opening path: "+path)
		
	dir.list_dir_begin()
	var current = dir.get_next()
	print(current)
	while not current.empty():
		if dir.current_is_dir():
			if !current.begins_with('.'):
				_delete_data(path+'/'+current)
		else:
			var removed = dir.remove(path+'/'+current)
			if !removed==OK:
				OS.alert("Error "+str(removed)+" deleting: "+current)
		current = dir.get_next()
	var deleted = dir.remove(path)
	if !deleted==OK:
		OS.alert("Error "+str(deleted)+" deleting: "+path)
	return deleted