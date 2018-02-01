import requests

headers = {
	'User-Agent': 'CurseForge Uploader Script/1.0',
	'X-API-Key': YOUR_KEY
}

files = {'file': ('MyFile.zip', open('MyFile.zip', 'r'))}
data = {
	'name': 'Version Banana',
	'game_versions': '181',
	'file_type': 'a',
	'change_log': 'This is a changelog',
	'change_markup_type': 'creole',
	'known_caveats': '',
	'caveats_markup_type': 'plain',
}

r = requests.post('http://wow.curseforge.com/addons/YOUR_PROJECT/upload-file.json', data = data, headers = headers, files = files)
print(r.content)