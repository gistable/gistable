import time
from datetime import datetime, date

# 今天
datetime.datetime.today().date().isoformat()

# 通过日期对象生成时间戳
int(time.mktime(datetime.now().timetuple()))

# 通过时间戳生成日期对象，timestamp 的时间戳以秒为单位
time.gmtime(timestamp) # GMT 0时区
time.localtime(timestamp) # 当前时区
datetime.fromtimestamp(time.mktime(time_struct)) #从time_struct生成时间对象

# 直接生成当前时间戳
int(1000 * time.time())

# 生成当前日期
today = date.today()

# 当作UTC时间戳转换
timeline = datetime.utcfromtimestamp(timestamp)
# 使用本地时区转换
timeline = datetime.fromtimestamp(timestamp)

# datetime 类型转换为 date 类型
timelime.date()

# 获取日期字符串 格式: 20130723
print datetime.today().date().isoformat().replace('-', '')

# 将GMT格式字符转转换成时间对象
time.strptime('Wed Aug 28 08:56:02 +0800 2013', '%a %b %d %H:%M:%S +0800 %Y')

# python库dateutil，可以自动转换时间和字符串，用起来太方便了，有这个库就不用上面说的那些麻烦的方法了
from dateutil.parser import parse
date = parse('Wed Aug 28 08:56:02 +0800 2013')

#django中获取utc时间戳
import datetime
from django.utils.timezone import utc
now = datetime.datetime.utcnow().replace(tzinfo=utc)