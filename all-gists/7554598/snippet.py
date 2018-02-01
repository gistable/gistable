import json

def combine_json():
    with open('j1.json') as file:
        d1 = json.loads(file.read())
    with open('j2.json') as file:
        d2 = json.loads(file.read())
    result = combine_dict(d1,d2)
    j3 = json.dumps(result)
    return j3

def combine_dict(j1,j2):
    result = j1.copy()
    for k,v in j2.iteritems():
        if k in result:
            #Both the values are strings
            if isinstance(result[k],unicode) and isinstance(v,unicode):
                if result[k].lower() == v.lower():
                    result[k] = v
                else:
                    result[k] = [result[k]]+[v]
            #either of them are strings
            elif isinstance(result[k],unicode) and isinstance(v,list):
                result[k] = List_String_Handler(v,result[k])
            elif isinstance(result[k],list) and isinstance(v,unicode):
                result[k] = List_String_Handler(result[k],v)
            elif isinstance(result[k],list) and isinstance(v,list):
                result[k] = result[k] + v
            elif isinstance(result[k],dict) and isinstance(v,dict):
                result[k] = combine_dict(result[k],v)
        else:
            result[k] = v

    print result
    return result

#When calling this method Parameter 'a' is always assumed to be a list and parameter 'b' to be string
def List_String_Handler(a,b):
    retr = list(set(a+[b]))
    retr.sort()
    return retr