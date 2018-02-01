	browser = request.user_agent.browser
	version = request.user_agent.version and int(request.user_agent.version.split('.')[0])
	platform = request.user_agent.platform
	uas = request.user_agent.string

	if browser and version:
		if (browser == 'msie' and version < 9) \
		or (browser == 'firefox' and version < 4) \
		or (platform == 'android' and browser == 'safari' and version < 534) \
		or (platform == 'iphone' and browser == 'safari' and version < 7000) \
		or ((platform == 'macos' or platform == 'windows') and browser == 'safari' and not re.search('Mobile', uas) and version < 534) \
		or (re.search('iPad', uas) and browser == 'safari' and version < 7000) \
		or (platform == 'windows' and re.search('Windows Phone OS', uas)) \
		or (browser == 'opera') \
		or (re.search('BlackBerry', uas)):
			return render_template('unsupported.html')