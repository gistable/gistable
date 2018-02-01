import requests

sites = get_sites_from_db()

for s in sites:
	try:
		r = requests.head(s)
		if r.status_code in [404,500]:
			remove_site_from_db(s)
	except Exception:
		continue