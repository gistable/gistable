# $ pip freeze
# elasticsearch==1.9.0
# requests-aws4auth==0.7
# requests==2.7.0
# certifi==2015.11.20.1

from elasticsearch import Elasticsearch
from elasticsearch.connection import RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import certifi
import os

def awsauth_wrapper(es_region):
    def awsauth(req):
        awsauth=AWS4Auth(os.environ['AWS_ACCESS_KEY_ID'], os.environ['AWS_SECRET_ACCESS_KEY'], es_region, 'es')
        req = awsauth(req)
        if 'AWS_SECURITY_TOKEN' in os.environ:
            req.headers['x-amz-security-token'] = os.environ['AWS_SECURITY_TOKEN']
        return req

    return awsauth

def aws_elasticsearch_client(host, es_region):
    return Elasticsearch([{
        'host': host,
        'port': 443
    }], connection_class=RequestsHttpConnection,
        http_auth=awsauth_wrapper(es_region),
        use_ssl=True,
        verify_certs=True,
        ca_certs=certifi.where()
    )
