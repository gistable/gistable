from urllib.request import urlopen
import json

gist_description = "does stuff"
gist_filename = 'file1_upload_to_github.py'
gist_body = """\
line1
line2
line3
line4
"""

def main_function(gist_filename, gist_description, gist_body):

    gist_post_data = {  'description': gist_description, 
                        'public': True,
                        'files': {gist_filename: {'content': gist_body}}}

    json_post_data = json.dumps(gist_post_data).encode('utf-8')

    def get_gist_url(found_json):
        wfile = json.JSONDecoder()
        wjson = wfile.decode(found_json)
        print('https://gist.github.com/' + wjson['id'])

    def upload_gist():
        print('sending')
        url = 'https://api.github.com/gists'
        json_to_parse = urlopen(url, data=json_post_data)
        
        print('received response from server')
        found_json = json_to_parse.readall().decode()
        get_gist_url(found_json)

    upload_gist()


main_function(gist_filename, gist_description, gist_body)
