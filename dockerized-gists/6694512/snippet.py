import sys
import simplejson as json


def get_param(js, param=()):

    if len(param) == 0:
        return None

    if len(param) == 1:
        return js.get(param[0], None)

    next_value = js.get(param[0], None)

    if next_value == None or type(next_value) != dict:
        return None

    return get_param(next_value, param[1:])

def parse_stream(stream, params):
    for line in stream:
        try:
            js = json.loads(line)

            values = [str(get_param(js, p.split('.'))) for p in params]

            print "Values: " + ' '.join(values)
        except:
            raise


if __name__ == '__main__':
    parse_stream(sys.stdin, (sys.argv[1:]))

