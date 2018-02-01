import numpy as np
import matplotlib.pyplot as plt

# それっぽいデータを作る処理
from datetime import datetime, timedelta
import scipy
import scipy.stats
def create_dummy_data(days):
    x = np.linspace(2, 2 + days, days)
    y = scipy.stats.norm.pdf(x, loc=0, scale=4) * 4 + 0.15
    y = y + np.abs(np.random.randn(len(y)))/25
    date = datetime.now().date() - timedelta(days=days)
    return {
        "date": date,
        "values": list(y)
    }
vals = map(create_dummy_data, np.arange(1, 30))
vals.reverse()

from matplotlib import dates

# 表示する経過日数
max_y = 35

# xはdatetimeからnumberに変換しておく
x = map(lambda v: dates.date2num(v['date']), vals)
# yは1(翌日)からスタート
y = np.arange(1, max_y + 1)
# xとyのメッシュを作成
Y, X = np.meshgrid(y, x)

def expand_z(v):
    v = v['values']
    v += list(np.zeros(max_y - len(v)))
    return v
# 縦横を揃えるためにゼロ埋め配列を追加する
z = map(expand_z, vals)
# numpyの行列に変換する
Z = np.array(z).reshape(len(z), len(z[0]))

fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(8, 4))

# プロットの作成
# データによって色が変わってしまうのを回避するため、最大値を指定
im = ax.pcolor(X, Y, Z, vmax=0.6)

# タイトル
ax.set_title(u'Launch Retention')
# y軸
ax.set_ylabel(u'Past Days')
ax.set_ylim(bottom=1)
# x軸
ax.set_xlim(x[0], x[-1])
# カラーバー
plt.colorbar(im)

# Ticks
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
minorLocator = MultipleLocator(5)
ax.xaxis.set_minor_locator(dates.DayLocator())
ax.xaxis.set_minor_formatter(dates.DateFormatter('%d'))
ax.xaxis.set_major_locator(dates.MonthLocator())
ax.xaxis.set_major_formatter(dates.DateFormatter('%Y %b'))
ax.xaxis.set_tick_params(which='major', pad=17)
plt.xticks(rotation=0)