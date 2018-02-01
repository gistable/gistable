import json

HTTP_METHODS = ['GET', 'POST', 'HEAD', 'PUT', 'DELETE', 'OPTIONS', 'CONNECT']


class ParseError(Exception):
    def __init__(self, msg):
        Exception.__init__(self)
        self.message = msg


def parse(raw_text: str):
    while True:  # get rid of empty lines
        if raw_text.startswith('\n'):
            raw_text = raw_text[1:]
        elif raw_text.endswith('\n'):
            raw_text = raw_text[:-1]
        else:
            break

    result = dict()
    lines = raw_text.split('\n')
    if lines[0].split(' ')[0] not in HTTP_METHODS:
        raise ParseError('Method not recognized')
    result['method'], url, result['version'] = lines[0].split(' ')

    if '?' in url:
        result['url'], query_str = url.split('?')
        query_params = dict()
        for item in query_str.split('&'):
            _k, _v = item.split('=', 1)
            query_params[_k] = _v
        result['query'] = query_params
    else:
        result['url'] = url
    if lines[-2] != '':  # no content
        headers = dict()
        for line in lines[1:]:
            _k, _v = line.split(': ', 1)
            if _k == 'Content-Length':
                continue
            headers[_k] = _v
        result['headers'] = headers
        return result
    content = lines[-1]
    result['content'] = content
    try:
        json_d = json.loads(content)
        result['json'] = json_d
    except:
        pass
    try:
        form = dict()
        for item in content.split('&'):
            _k, _v = item.split('=', 1)
            form[_k] = _v
        result['form'] = form
    except:
        pass
    headers = dict()
    for line in lines[1:-2]:
        _k, _v = line.split(': ', 1)
        if _k == 'Content-Length':
            continue
        headers[_k] = _v
    result['headers'] = headers
    return result


def main():
    raw_str = ''
    end = False
    while True:
        in_str = input()
        if in_str == '':
            if end:
                break
            end = True
        else:
            end = False
            if not raw_str:
                raw_str = in_str
            else:
                raw_str += '\n' + in_str
    print(json.dumps(parse(raw_str), indent=2))


if __name__ == '__main__':
    main()
