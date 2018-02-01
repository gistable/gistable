from flask import Response

RE_API_DOCS_BASE_PATH = re.compile(r'"basePath": "(.*)\/api\/')
API_SANDBOX_URL = '"basePath": "http://localhost:5000/api/'

@app.route('/api/v1/api-docs', methods=['GET'])
def api_docs_index():
    return Response(RE_API_DOCS_BASE_PATH.sub(API_SANDBOX_URL,
                    open('./docs/api/v1/index.json').read()),
                    mimetype='application/json')


@app.route('/api/v1/api-docs/<resource>', methods=['GET'])
def api_docs(resource):
    return Response(RE_API_DOCS_BASE_PATH.sub(API_SANDBOX_URL,
                    open('./docs/api/v1/{}.json'.format(resource)).read()),
                    mimetype='application/json')
