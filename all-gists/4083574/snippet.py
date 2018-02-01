# encoding: utf-8
from pylab import *

def XDiff(x, y, a):
    return -a * x + y #Griffithモデル

def YDiff(x, y, b):
    return x **2/ (1.0+ x **2) - b * y

def XNull(x, a): #xヌルクライン
    return a * x

def YNull(x, b): #yヌルクライン
    return x **2/ (b * (1.0+ x **2))

def checkStablePoint(a, b, x): #det(J)が正かどうか確かめる
    if a * b > 2* x / (1.0+ x **2) **2:
        return "ko" #安定
    else:
        return "wo" #不安定

x  = arange(0, 5.0, 0.1) #タンパク質濃度の定義域
a = [0.5, 1, 2] #タンパク質の分解速度。ab <=> 0.5となるようにする
b = 0.5 #mRNAの分解速度。ここでは1固定
xNull = [] #xについてのヌルクラインを作成する
yNull = YNull(x, b)

for i in a:
    xNull.append(XNull(x, i))
"""#1つ目の固定点解析 numpy.sqrt
figure()
xlim(0, 4)
ylim(0, 2)
plot(x, yNull)
plot(x, xNull[0])
plot(0, xNull(0, a[0]), checkStablePoint(a[0], b, 0), markersize =10)
plot(2- sqrt(3), XNull(2- sqrt(3), a[0]), checkStablePoint(a[0], b, 2- sqrt(3)), markersize =10)
plot(2+ sqrt(3), XNull(2+ sqrt(3), a[0]), checkStablePoint(a[0], b, 2+ sqrt(3)), markersize =10)
#2つ目の固定点解析
figure()
xlim(0, 4)
ylim(0, 2)
plot(x, yNull)
plot(x, xNull[1])
plot(0, xNull(0, a[1]), checkStablePoint(a[1], b, 0), markersize =10)
plot(1, xNull(1, a[1]), checkStablePoint(a[1], b, 1), markersize =10)
#3つ目の固定点解析
figure()
xlim(0, 4)
ylim(0, 2)
plot(x, yNull)
plot(x, xNull[2])
plot(0, xNull(0, a[2]), checkStablePoint(a[2], b, 0), markersize =10)

for i in range(3):
    figure()
    xlim(0, 4)
    ylim(0, 2)
    plot(x, yNull)
    plot(x, xNull[i])
    
    for j in arange(0, 4.2, 0.2):
        for k in arange(0, 2.1, 0.1):
            quiver(j, k, XDiff(j, k, a[i]), YDiff(j, k, b))

#1つ目: ab = 0.25
figure() #新たな描画面を作成
xlim(0, 4) #範囲指定
ylim(0, 2)
plot(x, yNull)
plot(x, xNull[0]) #以下ベクトル場を作成
quiver(0.2, XNull(0.2, a[0]), 0, YDiff(0.2, XNull(0.2, a[0]), b))
quiver(0.2, YNull(0.2, b), XDiff(0.2, YNull(0.2, b), a[0]), 0)
quiver(1, XNull(1, a[0]), 0, YDiff(1, XNull(1, a[0]), b))
quiver(1, YNull(1, b), XDiff(1, YNull(1, b), a[0]), 0)
quiver(4, XNull(4, a[0]), 0, YDiff(4, XNull(4, a[0]), b))
quiver(4, YNull(4, b), XDiff(4, YNull(4, b), a[0]), 0)

#2つ目: ab = 0.5
figure() #新たな描画面を作成
xlim(0, 4) #範囲指定
ylim(0, 2)
plot(x, yNull)
plot(x, xNull[1]) #以下ベクトル場を作成
quiver(0.5, XNull(0.5, a[1]), 0, YDiff(0.5, XNull(0.5, a[1]), b))
quiver(0.5, YNull(0.5, b), XDiff(0.5, YNull(0.5, b), a[1]), 0)
quiver(2, XNull(2, a[1]), 0, YDiff(2, XNull(2, a[1]), b))
quiver(2, YNull(2, b), XDiff(2, YNull(2, b), a[1]), 0)

#3つ目: ab = 0.1
figure() #新たな描画面を作成
xlim(0, 4) #範囲指定
ylim(0, 2)
plot(x, yNull)
plot(x, xNull[2]) #以下ベクトル場を作成
quiver(1, XNull(1, a[2]), 0, YDiff(1, XNull(1, a[2]), b))
quiver(1, YNull(1, b), XDiff(1, YNull(1, b), a[2]), 0)
"""
figure()
xlim(0, 4)
ylim(0, 2)
plot(x, yNull)

for i in xNull:
    plot(x, i)

show() #全figure描画
