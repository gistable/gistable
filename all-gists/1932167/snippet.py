#!usr/bin/env/ python
#-*- coding:utf-8 -*-
"""
---------------------------------------------------------------------
ある時刻(0時〜23時)が、指定した時間の範囲内に含まれるかどうかを調べる
プログラムを作ってください。
言語は問いませんが、ライブラリなどを使ってはいけません。
以下のような条件を満たすこと
- ある時刻と、時間の範囲(開始時刻と終了時刻)を受け取る。
- 時刻は、6時であれば6のような指定でよく、分単位は問わない。
- 範囲指定は、開始時刻を含み、終了時刻は含まないと判断すること。
- ただし開始時刻と終了時刻が同じ場合は含むと判断すること。
- 開始時刻が22時で終了時刻が5時、というような指定をされても動作すること。
--------------------------------------------------------------------
"""

#input
stime = int(raw_input('input start time(0~23) =>'))
ftime = int(raw_input('input finish time(0~23) =>'))
ttime = int(raw_input('input time(0~23) to judge =>'))

def judge(time,start,finish):
	result = ''
	if start <= finish:
		if start <= time < finish or start == time == finish:
			result = 'true'
	else:
		if not finish <= time < start:
			result = 'true'
	if result == 'true':
		return time,'is included between',start,'and',finish
	else:
		return time,'is not included between',start,'and',finish

#output
print judge(ttime,stime,ftime)
