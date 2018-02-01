#coding=utf-8
import time
import sched
import os
import threading
"""
sched模块，准确的说，它是一个调度（延时处理机制），每次想要定时执行某任务都必须写入一个调度。
使用步骤如下：
(1)生成调度器：
s = sched.scheduler(time.time,time.sleep)
第一个参数是一个可以返回时间戳的函数，第二个参数可以在定时未到达之前阻塞。可以说sched模块设计者是
“在下很大的一盘棋”，比如第一个函数可以是自定义的一个函数，不一定是时间戳，第二个也可以是阻塞socket等。
(2)加入调度事件
其实有enter、enterabs等等，我们以enter为例子。
s.enter(x1,x2,x3,x4)
四个参数分别为：间隔事件、优先级（用于同时间到达的两个事件同时执行时定序）、被调用触发的函数，给他的
参数（注意：一定要以tuple给如，如果只有一个参数就(xx,)）
(3)运行
s.run()
注意sched模块不是循环的，一次调度被执行后就Over了，如果想再执行，请再次enter
"""
##########################
#初始化sched模块的scheduler类
##########################
s = sched.scheduler(time.time,time.sleep)

##########################
#调度函数定义
##########################
def event_func(name,start):
	"""
	触发调度函数
	"""
	now=time.time()
	elapsed=int(now-start)
	print 'EVENT: %s elapsed= %s name= %s' % (time.ctime(now),elapsed,name)

###############################################################
#定义执行函数，并通过enter函数加入调度事件
#enter四个参数分别为：间隔事件、优先级（用于同时间到达的两个事件同时执行时定序）,
#被调用触发的函数，给他的参数（注意：一定要以tuple给如，如果只有一个参数就(xx,)）
###############################################################

def perform(inc,name,start):
	"""
	实现60s周期执行任务
	"""
	s.enter(inc,0,perform,(inc,name,start))
	event_func(name,start)

#######################
#主函数入口
#######################
def mymain(inc=60):
	"""
	入口主函数
	"""
	start = time.time()
	print('START:',time.ctime(start))
	#设置调度
	e1 = s.enter(2,1,perform,(inc,'first',start))                             #调度设置
	e2 = s.enter(3,1,perform,(inc,'second',start))
	e3 = s.enterabs(start+5,2,perform,(inc,'first',start))              #设置调度优先级，enterabs()保证同时性
	e4 = s.enterabs(start+5,1,perform,(inc,'second',start))
	#启动线程
	t=threading.Thread(target=s.run)                                        #通过构造函数例化线程
	t.start()                                                                                    #线程启动
	s.cancel(e2)                                                                            #取消任务调度e2
	t.join()                                                                                     #阻塞线程

#########################
#测试代码
if __name__ == "__main__":
	mymain() 