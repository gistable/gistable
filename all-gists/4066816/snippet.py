def read_only_processor(request):
	if read_only_flag():
		if request.method in ['GET', 'HEAD']:
			return {
				'read_only': True, 
				'error_message': 'Sorry, this site is read only right now!"
				}
		else:
			#return a "Read only" response
	else:
		return {'read_only': False, 'error_message': ''}
	