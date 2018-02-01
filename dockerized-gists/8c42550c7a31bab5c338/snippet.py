#!/user/bin/python 
import json

class DocumentBase(object):
    
    def traversal_for_init_dict(self, items):
        for k in items:
            if type(items[k]) == dict:
                setattr(self, k, DocumentDict(**items[k]))
            elif type(items[k]) == list:
                setattr(self, k, self.traversal_for_init_list(items[k]))
            else:
                setattr(self, k, items[k])
        return self.__dict__

    def traversal_for_init_list(self, items):
        rc = []
        for n in xrange(len(items)):
            if type(items[n]) == list:
                rc.append(self.traversal_for_init_list(items[n]))
            elif type(items[n]) == dict:
                rc.append(DocumentDict(**items[n]))
            else:
                rc.append(items[n])
        return rc

    def traversal_to_dict(self, rc, items):
        for k in items:
            if type(items[k]) == DocumentDict:
                rc[k] = items[k].to_dict()
            elif type(items[k]) == list:
                rc[k] = self.traversal_to_list(items[k])
            else:
                rc[k] = items[k]

    def traversal_to_list(self, items):
        rc = [] 
        for k in xrange(len(items)):
            if type(items[k]) == list:
                rc.append(self.traversal_to_list(items[k]))
            elif type(items[k]) == DocumentDict:
                rc.append(items[k].to_dict())
            else:
                rc.append(items[k])
        return rc


class DocumentDict(DocumentBase):

    def __init__(self, **kwargs):
        self.traversal_for_init_dict(kwargs)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    def to_dict(self):
        rc = {}
        self.traversal_to_dict(rc, self.__dict__)
        return rc


class DocumentList(DocumentBase):
    
    def __init__(self, items):
        if type(items) != list: 
            raise Exception("not list: %s" % str(items))
        self.__list__ = self.traversal_for_init_list(items)

    def __getitem__(self, index):
        return self.__list__[index]

    def to_dict(self):
        return self.traversal_to_list(self.__list__)


if __name__ == '__main__':


    print 'test...'

    test_case = {
            "a": 1,
            "b": 12.0,
            "c": 'cccc',
            "d": { "d1": 3333, "d2": "xxx"},
            "e": [
                    {"e1": 6666},
                    {"e2": 8888, "e3": { "e31":-1, "e32":[ "ss1", "ss2"] } },
                    {"e4": [100, 200, 300] }
                ],
            "f": [ [0, 1, 3], ['a', 'b'], [ {"f1":1}, {"f2": 2}  ]]
            }

    test_case_list = [ test_case, test_case, test_case]

    print json.dumps(test_case) 
    print json.dumps(test_case_list)
    print 100, '='*80

    dd = DocumentDict()

    dd2 = DocumentDict()
    dd2.aaa_x=1
    dd2.bbb_y=2

    dd.a = 1
    dd.b = '2'
    dd.c = []
    dd.d = dd2

    dd.c.append(dd2)
    dd.c.append(dd2)
    dd.c.append(dd2)

    #print dd.a, dd.b, dd.c, dd.d
    print dd.to_dict()
    print 111, '='*80

    dd3 = DocumentDict(**test_case)
    print dd3.to_dict()

    print 222, '='*80
    print dd3.a, dd3.b, dd3.d, dd3.e, dd3.d.d1, dd3.d.d2

    print dd3.e[0].e1
    print dd3.e[1].e2, dd3.e[1].e3.e31, dd3.e[1].e3.e32, dd3.e[1].e3.e32[0]
    print dd3.e[2].e4, dd3.e[2].e4[0]
    print dd3.f[0], dd3.f[2][0].f1, dd3.f[2][1].f2

    print 333, '='*80
    ddl = DocumentList(test_case_list)
    print ddl.to_dict()

    print ddl[0].e[0].e1, ddl[1].e[1].e2

    DocumentDict()

    print 'done'






