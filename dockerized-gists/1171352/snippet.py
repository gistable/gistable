def dados_do_local(endereco):
	"""
	Dado o endereco, retorna o endereco processado, a latitude e a longitude do local.
        Exemplo:
         place, (lat, lng) = dados_do_local(endereco)
	"""
	from geopy import geocoders
	if hasattr(settings, "EASY_MAPS_GOOGLE_KEY") and settings.EASY_MAPS_GOOGLE_KEY:
		g = geocoders.Google(settings.EASY_MAPS_GOOGLE_KEY)
	else:
		g = geocoders.Google(resource='maps')
	return g.geocode(endereco)  