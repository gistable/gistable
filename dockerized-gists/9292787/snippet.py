import urlparse
import json
import requests

# set your api key for this work
apikey = 'XXXXX'
datapusher_url = 'http://datapusher-test.herokuapp.com'
ckan_url = 'http://datahub.io'
# gold prices
res_id = 'b9aae52b-b082-4159-b46f-7bb9c158d013'

res = requests.post(
        urlparse.urljoin(datapusher_url, 'job'),
        headers={
            'Content-Type': 'application/json'
        },
        data=json.dumps({
            'api_key': apikey,
            'job_type': 'push_to_datastore',
            'result_url': '',
            'metadata': {
                'ckan_url': ckan_url,
                'resource_id': res_id,
                'set_url_type': False
            }
        })
    )

print res.status_code
print res.json()

data = res.json()
job_url = datapusher_url + '/job/' + data['job_id']

print('curl -H "Authorization: %s" %s' % (data['job_key'], job_url))
