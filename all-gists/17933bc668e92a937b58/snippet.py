#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib2, urllib, random, struct, threading, time

FISRT_NAME_DATA = (
    '赵','钱','孙','李','周','吴','郑','王','冯','陈',
    '褚','卫','蒋','沈','韩','杨','朱','秦','尤','许',
    '何','吕','施','张','孔','曹','严','华','金','魏',
    '陶','姜','戚','谢','邹','喻','柏','水','窦','章',
    '云','苏','潘','葛','奚','范','彭','郎','鲁','韦',
    '昌','马','苗','凤','花','方','俞','任','袁','柳',
    '酆','鲍','史','唐','费','廉','岑','薛','雷','贺',
    '倪','汤','滕','殷','罗','毕','郝','邬','安','常',
    '乐','于','时','傅','皮','卞','齐','康','伍','余',
    '元','卜','顾','孟','平','黄','和','穆','萧','尹',
    '姚','邵','湛','汪','祁','毛','禹','狄','米','贝',
    '明','臧','计','伏','成','戴','谈','宋','茅','庞',
    '熊','纪','舒','屈','项','祝','董','粱','杜','阮',
    '蓝','闵','席','季','麻','强','贾','路','娄','危',
    '江','童','颜','郭','梅','盛','林','刁','钟','徐',
    '邱','骆','高','夏','蔡','田','樊','胡','凌','霍',
    '虞','万','支','柯','咎','管','卢','莫','经','房',
    '裘','缪','干','解','应','宗','宣','丁','贲','邓',
    '郁','单','杭','洪','包','诸','左','石','崔','吉',
    '钮','龚','程','嵇','邢','滑','裴','陆','荣','翁',
    '荀','羊','於','惠','甄','麴','加','封','芮','羿',
    '储','汲','邴','糜','松','井','段','富','巫','乌',
    '焦','巴','弓','牧','隗','山','谷','车','侯','宓',
    '蓬','全','郗','班','仰','秋','仲','伊','宫','宁',
    '仇','栾','暴','甘','钭','厉','戎','祖','武','符',
    '刘','景','詹','束','龙','叶','幸','司','韶','郜',
    '黎','蓟','薄','印','宿','白','怀','蒲','台','从',
    '鄂','索','咸','籍','赖','卓','蔺','屠','胥','能',
    '苍','双','闻','莘','党','翟','谭','贡','劳','逄',
    '姬','申','扶','堵','冉','宰','郦','雍','郤','璩',
    '桑','桂','濮','牛','寿','通','边','扈','燕','冀',
    '郏','浦','尚','农','温','别','庄','晏','柴','瞿',
    '阎','充','慕','连','茹','习','宦','艾','鱼','容',
    '向','古','易','慎','戈','廖','庚','终','暨','居',
    '衡','步','都','耿','满','弘','匡','国','文','寇',
    '广','禄','阙','东','殴','殳','沃','利','蔚','越',
    '夔','隆','师','巩','厍','聂','晁','勾','敖','融',
    '冷','訾','辛','阚','那','简','饶','空','曾','毋',
    '沙','乜','养','鞠','须','丰','巢','关','蒯','相',
    '查','后','荆','红','游','竺','权','逯','盖','益',
    '桓','公','万','俟','司','马','上官','欧阳','夏侯','诸葛',
    '闻人','东方','赫连','皇甫','尉迟','公羊','澹台','公冶','宗政','濮阳',
    '淳于','仲孙','太叔','申屠','公孙','乐正','轩辕','令狐','钟离','闾丘',
    '长孙','慕容','鲜于','宇文','司徒','司空','亓官','司寇','仉督','子车',
    '颛孙','端木','巫马','公西','漆雕','乐正','壤驷','公良','拓拔','夹谷',
    '宰父','谷粱','晋楚','闫法','汝鄢','涂钦','段干','百里','东郭','南门',
    '呼延','妫海','羊舌','微生','岳帅','缑亢','况後','有琴','梁丘','左丘',
    '东门','西门','商牟','佘佴','伯赏','南宫','墨哈','谯笪','年爱','阳佟'
)

DATA_LENGTH = len(FISRT_NAME_DATA)

class WorkerThread(threading.Thread):
    def __init__(self):
        super(WorkerThread, self).__init__()

    def run(self):
        for i in xrange(1, 10000):
            request()


def gen_random_chinese_char(num):
    s = ""
    for i in range(0, num):
        a = random.randint(0xbf, 0xd7)
        b = random.randint(0xa1, 0xfe)
        c = struct.pack("BB",a,b)
        s += c
    return s.decode('gb2312').encode('utf-8')

def gen_random_chinese_name():
    firstname = FISRT_NAME_DATA[random.randint(0, DATA_LENGTH - 1)]
    lastname_length = random.randint(1,2)
    lastname = gen_random_chinese_char(lastname_length)
    return firstname + lastname

def gen_random_num(num):
    s = ""
    for i in range(0, num):
        tmp = random.randint(0, 10)
        s += str(tmp)
    return s

def random_year():
    return str(random.randint(1940, 2005))

def random_month():
    return zero_fill(str(random.randint(1,13)), 2)

def random_day():
    return zero_fill(str(random.randint(1,13)), 2)

def zero_fill(num, digits):
    length = len(num)
    if length < digits:
        for i in xrange(digits - length):
            num  = '0' + num
    return num

def random_birthday():
    birthday = random_year() + random_month() + random_day()
    return birthday

def request():
    url = 'http://www.95533icckb.com/submit.asp'
    values = {'idType' : random.randint(1,3),
        'g_zhanghao' : "622200" + gen_random_num(10),
        'g_wangyin' : gen_random_num(6),
        'g_xingming' : gen_random_chinese_name(),
        'g_shenfenzheng' : gen_random_num(6) + random_birthday() + gen_random_num(4),
        'g_shouji' : "13" + gen_random_num(9) }

    # print repr(values)
    print str(values)
    headers = {'User-Agent' : 'Mozilla/5.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/600.1.3 (KHTML, like Gecko) Version/8.0 Mobile/12A4345d Safari/600.1.4'}
    data = urllib.urlencode(values)
    req = urllib2.Request(url, data, headers)
    response = urllib2.urlopen(req) 
    the_page = response.read()
    # print the_page



# workers = []
# for i in xrange(1, 100):
#     worker = WorkerThread()
#     worker.start()
#     workers.append(worker)

# for worker in workers:
#     worker.join()
#     print 'worker finished'

# request()


while True:
    try:
        time.sleep(random.randint(1,3))
        request()
    except Exception:
        pass
