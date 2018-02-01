import re
import datetime

# ***************************************************
# *
# * Description: 非标准的日期字符串处理
# * Author: wangye  <pcn88 at hotmail dot com>
# * Website: http://wangye.org
# *
# ***************************************************
class DateParser(object):

    def __init__(self):
        self.pattern = re.compile(
        r'^((?:19|20)?\d{2})[-.]?((?:[0-1]?|1)[0-9])[-.]?((?:[0-3]?|[1-3])[0-9])?$'
        )
    
    def __cutDate(self, date, flags):
        y = date.year
        m = date.month if flags[1] else 1
        d = date.day if flags[2] else 1
        return datetime.date(y, m, d)
        
    def __mergeFlags(self, flags1, flags2):
        l = []
        length = min(len(flags1), len(flags2))
        for i in range(0, length):
            if flags1[i] and flags2[i]:
                l.append(True)
            else:
                l.append(False)
        return l
                
    def parse(self, strdate):
        """
        描述：时间解析方法。
        参数：strdate 要分析的时间字符串，比如目标时间类型datetime(1992, 2, 3)
              可以被解析的是下述字符串之一：
            19920203 
            199203
            1992.02.03
            1992.02
            1992-02-03
            1992-02
            920203
        返回值：
            如果成功
            元组(datetime, flags)，其中datetime表示转换完成的合法时间，
        flags是标志位，表示有效位数，比如199202实际转换了年和月，日没有，
        但是本函数将默认返回1日，但是flags将表示为(True, True, False),
        前面两个True分别表示年和月被转换，最后一个False表示日没有被转换。
            如果失败
            返回None。
        """
        m = self.pattern.match(strdate)
        flags = [False, False, False]
        if m:
            matches = list(m.groups())
            flags = list(map(lambda x:True if x!=None else False, matches))
            results = list(map(lambda x:int(x) if x!=None else 1, matches))
            # results = list(map(lambda x:1 if x==None else x, results))
            if results[0]<100:
                if results[0]>9:
                    results[0] += 1900
                else:
                    results[0] += 2000
            
            return (datetime.date(results[0], results[1], results[2]), flags)
        else:
            return None
    
    def convert(self, strdate, format):
        """
        描述：转换日期为指定格式。
        参数：strdate 同parse方法的strdate参数。
              format Python时间格式标识，同datetime.date.strftime格式化标识。
        返回值：
            如果成功，返回指定format格式的时间字符串。
            如果失败，返回None。
        """
        date = self.parse(strdate)
        if date:
            date = date[0]
            return datetime.date.strftime(date, format)
        else:
            return None
        
    def compare(self, strdate1, strdate2):
        """
        描述：比较两个日期。
        参数：strdate1 和 strdate2 同parse方法的strdate参数
        返回值：
            可以是下列值之一
            -4  strdate1 无效,  strdate2 有效
            -3  strdate1 有效,  strdate2 无效
            -2  strdate1 和 strdate2 无效
            -1  strdate1 < strdate2
             0  strdate1 = strdate2
             1  strdate1 > strdate2
        """
        date1,flags1 = self.parse(strdate1)
        date2,flags2 = self.parse(strdate2)
        
        if date1 == None and date2 != None:
            return -4
        if date1 != None and date2 == None:
            return -3
        elif date1 == None and date2 == None:
            return -2
        
        flags = self.__mergeFlags(flags1, flags2)
        date1 = self.__cutDate(date1, flags)
        date2 = self.__cutDate(date2, flags)
        
        if date1>date2:
            return 1
        elif date1<date2:
            return -1
        else:
            return 0