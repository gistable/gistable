#!python
#-*-coding:utf8-*-
'''
Стоянов Евгений quick.es@gmail.com
Модуль для удобного обмена с 1С:Предприятие 8.Х
Позволяет сформировать в строку списки и таблицы значений для дальнейшего восставновления в 1С.

Массив
{"#",51e7a0d2-530b-11d4-b98a-008048da3034,
{2,
{"S","12312"},
{"S","33333!фждыло"}
}
}

СписокЗначений
{"#",4772b3b4-f4a3-49c0-a1a5-8cb5961511a3,
{6,1e512aab-1b41-4ef6-9375-f0137be9dd91,0,0,
{2,
{1e512aab-1b41-4ef6-9375-f0137be9dd91,
{"таблица1",0,
.....
},
{3,0,
{0},"",-1,-1,0,0},0}
},
{1e512aab-1b41-4ef6-9375-f0137be9dd91,
{"название",0,
{"S","что то"},
{3,0,
{0},"",-1,-1,0,0},1}
}
},
{"Pattern"},0,1}
}

ТаблицаЗначений
{"#",acf6192e-81ca-46ef-93a6-5a6968b78663,
    {8,
        {3<колво колонок>,
            {-2,"НомерСтроки",
                {"Pattern",
                    {"N"}
                },"N",10
            },
            {0,"Реквизит1",
                {"Pattern",
                    {"S",10,1}
                },"Реквизит1",10
            },
            {1,"field2",
                {"Pattern",
                  {"S"}
                },"Field2",10
            }
        },
        {2,3<колво колонок>,0<порядк. номер>,-2<кол ном строки>,1,0<Реквизит1>,2,1<field2>,
*       {2,3,0,-2,1,0,2,1,      - 3 кол
*       {2,4,0,-2,1,0,2,1,3,2,  - 4 колонки)
*       {2,2,0,-2,1,0,          - 1 колонка
            {1,3<колво строк>,
                {2,0,3<колво колнок>,
                    {"N",1},
                    {"S","asdfasdfas"},
                    {"S","2983798236"},0
                },
                {2,1,3,
                    {"N",2},
                    {"S",";:\/*--+/."},
                    {"S","wer23"},0
                },
                {2,2,3,
                    {"N",3},
                    {"S","'sadf""sdfa"},
                    {"S","'[]"""""},0
                }
            },-1,2<колво-1>
        }
    }
}

'''
headPattern=\
u'{"#",acf6192e-81ca-46ef-93a6-5a6968b78663,\n\
{8,\n\
{%(ncols)s,\n\
{-2,"НомерСтроки",\n\
{"Pattern",\n\
{"N"}\n\
},"N",10}'

colheadPattern=\
u',\n\
{%(colnum0)s,"%(colname)s",\n\
{"Pattern",\n\
{"S"}\n\
},"%(colcaption)s",10}'

lineHeadPattern=\
u'{2,%(colnum0)s,%(ncols)s,\n'
lineRowStartPattern=\
u'{"N",%(colnum1)s},'
lineItemPattern=\
u'\n{"S","%(value)s"},'

lineEndPattern=\
u'0},\n'

NamedListItemPattern=\
u'{1e512aab-1b41-4ef6-9375-f0137be9dd91,\n\
{"%(name)s",0,\n\
{"S","%(value)s"},\n\
{3,0,\n\
{0},"",-1,-1,0,0},%(num0)s}\n\
},\n'

class V8Array(list):
    def export(self):
        res = '{"#",51e7a0d2-530b-11d4-b98a-008048da3034,\n{%s' % len(self)
        if len(self)>0:
            res += ','
        else:
            return res + '}\n}'

        for i in self:
            if i.__class__ in (V8ValueList,V8Table):
                value = i.export()
                res += value + ',\n'
            else:
                value = str(i).replace('"','""')
                res += '{"S","%s"},\n' % value
        res = res[:-2]
        res += '}\n}'
        return res


class V8ValueList(dict):
    def __init__(self,baseDict={}):
        self.head=u'{"#",4772b3b4-f4a3-49c0-a1a5-8cb5961511a3,\n'+\
                u'{6,1e512aab-1b41-4ef6-9375-f0137be9dd91,0,0,\n'+\
                u'{%(count)s,\n';
        if len(baseDict)>0:
            self.copyFrom(baseDict)

    def add(self,value,name):
        self[name] = value
        #{"таблица1",0,'
    def copyFrom(self,dictsrc):
        for item in dictsrc.items():
            self[item[0]] = item[1]

    def export(self):
        self.txt = self.head % {'count':len(self)}
        i=0
        for item in self.items():
            value = item[1]
            if value.__class__ in (str,unicode):
                value = value.replace('"','""')
            self.txt += NamedListItemPattern % {'name':item[0],'value':value,'num0':i}
            i+=1
        self.txt = self.txt[:-2]+u'\n},\n{"Pattern"},0,1}\n}'
        return self.txt

class V8Table:
    def __init__(self,_columns=[]):
        self.columns = _columns
        self.lines=u''
        self.head = u''
        self.lineno=0
        self.__v8_makeheader__()
    def add(self,line):
        '''
        line = {'col':val} or ['val1','val2']
        '''
        self.lines  += self.__v8_makerow__(line)
        self.lineno +=1
    def append_all(self,_list_of_dict):
        for item in _list_of_dict:
            if item.__class__==dict:
                self.add(item.values())
            elif item.__class__==list:
                self.add(item)

    def ncols(self):
        return len(self.columns)+1
    def save(self,filename):
        pass
    def __v8_makeheader__(self):
        self.head = headPattern % {'ncols':self.ncols()}
        i = 0
        headtail = u'0,-2,'
        for col in self.columns:
            #colhead = colheadPattern % {'colname':col,'colcaption':'col%s'%i}
            colhead = colheadPattern % {'colnum0':i,'colname':col,'colcaption':col}
            self.head += colhead
            headtail += u'%s,%s,'%(i+1,i)
            i+=1
        self.head += u'\n},\n'
        #{2,3<колво колонок>,0<порядк. номер>,-2<кол ном строки>,1,0<Реквизит1>,2,1<field2>,
        self.head += u'{2,%(colcount)s,' % {'colcount':self.ncols()}
        self.head += headtail
        return self.head
    def __v8_makerow__(self,row):
        line = lineHeadPattern % {'colnum0':self.lineno,'ncols':self.ncols()}
        line +=lineRowStartPattern % {'colnum1':self.lineno+1}
        #for i in xrange(0,len(self.columns)):
        for value in row:
            value_ = (u'%s'%value).replace('"','""')
            if value_.endswith('.0'):
                value_ = value_[:-2]
            line += lineItemPattern % {'value':value_}
        line += lineEndPattern
        return line
    def export(self):
        '''
        возращает структуру пригодную для загрузки в 1С в качетсве таблицы значений
        '''
        self.txt = self.head
        self.txt +=u'\n{1,%s,\n' % self.lineno \
                  + self.lines[:-2] + u'\n},-1,%s}\n}\n' % (self.lineno-1)
        self.txt += u'}'
        return self.txt

def _test_args(*args):
    print list(args)

def _test_head():
    v8=V8Export(['test1','test2','test3'])
    print v8.__v8_makeheader__()
def _test_lines():
    v8=V8Export(['test1','test2','test3'])
    print v8.__v8_makeheader__()
    v8.add(['102','2323','test'])
    v8.add(['1099','000','asd'])
    print v8.lines

def _test_all():
    v=V8Table(['test1','test2','test3'])
    v.add(['000','000','000"test"'])
    #v8.add('1099','000','asd')
    print v.export().encode('cp1251')
def _test_vallist():
    v=V8ValueList()
    v.add('value1','name1')
    print v.export()
def _test_array():
    ar = V8Array()
    ar.append('123123')
    print 'array',ar.export()
def main():
    #_test_head()
    #_test_lines()
    _test_all()
    _test_vallist()
    _test_array()
    #_test_args('asdf','234')
    t=''
    for i in range(100):
        t+='t%s,'%i
    print t
if __name__ == '__main__':
    main()
