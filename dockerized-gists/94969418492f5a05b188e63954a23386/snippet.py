def parse_dynamo_item(item):
    resp = {}
    if type(item) is str:
        return item
    for key,struct in item.iteritems():
        if type(struct) is str:
            if key == 'I':
                return int(struct)
            else:
                return struct
        else:
            for k,v in struct.iteritems():
                if k == 'L':
                    value = []
                    for i in v:
                        value.append(parse_dynamo_item(i))
                elif k == 'S':
                    value = str(v)
                elif k == 'I':
                    value = int(v)
                elif k == 'M':
                    value = {}
                    for a,b in v.iteritems():
                        value[a] = parse_dynamo_item(b)
                else:
                    key = k
                    value = parse_dynamo_item(v)

                resp[key] = value

    return resp