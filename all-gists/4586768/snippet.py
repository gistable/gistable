for u in User.objects.all():
	if u.email not in ['msn@antonagestam.se','appel268576@gmail.com']:
		u.email = '%s@example.com' % u.username
		u.save()