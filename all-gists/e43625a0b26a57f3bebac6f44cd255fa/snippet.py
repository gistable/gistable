#!/usr/bin/python
# -*- coding: utf-8 -*-

#各駅間の隣接リストを定義する。
#参考 http://www.geocities.jp/m_hiroi/light/pyalgo05.html ●隣接行列と隣接リスト
station_adjacent_dic = {
                    #山手線
                    'shinagawa':['tokyo', 'shibuya', 'kawasaki'],
                    'shibuya':['shinagawa', 'shinjuku'],
                    'shinjuku':['shibuya', 'ikebukuro'],
                    'ikebukuro':['shinjuku', 'tabata'],
                    'tabata':['ikebukuro', 'ueno'],
                    'ueno':['tabata', 'tokyo'],
                    'tokyo':['ueno', 'shinagawa'],

                    #京浜東北線
                    'kawasaki':['shinagawa','yokohama'],
                    'yokohama':['kawasaki']
                    }

#参加者情報（名前をkeyとし、現在地をvalueとするデータ構造）のリスト
member_dic = {'A':'kawasaki', 'B':'shinagawa', 'C':'ikebukuro', 'D':'ueno', 'E':'yokohama'}

#何駅先まで探索するか
MAX_ALLOW_COST=5
#探索対象外となった時のダミーのコスト値
MAX_DUMMY_COST=9999




# 目的駅へ到達するための経路を求め、経由駅数を返す。
# limit駅数内に目的駅へ到達できない場合は、-1を返す。
# 参考 http://www.geocities.jp/m_hiroi/light/pyalgo05.html ●反復深化のプログラム
#
# limit 探索対象とする経由駅数上限
# goal 経由駅数をカウントする目的駅
# path goalまでの駅の経路 （例'tokyo' -> 'shinagawa' -> 'shibuya'など）
def calc_cost(limit, goal, path):
    n = len(path)
    start = path[n - 1]
    cost = -1 #初期化
    if n >= limit:
        if start == goal:
            #goalまでのpathの経由駅数を返す
            return len(path)
        else:
            #探索したもののlimitの範囲ないにgoalがなかった
            return -1
    else:
        for adjacent_station in station_adjacent_dic[start]:
            path.append(adjacent_station)
            #隣接駅からさらに再帰的に探索する。
            cost = calc_cost(limit, goal, path)
            path.pop()
            if cost > 0:
                #経路が見つかったら抜ける。
                break
    return cost


#ここからがメイン処理
print 'debug文0:各メンバーの開始駅は、以下の通り', member_dic
print ''
result={}
print 'debug文1:各メンバーの各駅までのコスト'
for member_key in sorted(member_dic):
    #各メンバー毎に各駅へのコストを計算する。
    start = member_dic[member_key]
    #開始駅をpathの形式になるよう['tokyo']などの配列型にする。
    path = [start]
    result_row = {}
    for goal in station_adjacent_dic.keys():
        #各駅へのコスト計算
        for limit in range(1, MAX_ALLOW_COST):
            cost = calc_cost(limit, goal, path)
            if cost > 0:
                print member_key, 'は', start, 'から', goal, 'まで', cost-1, '駅' #costは開始駅もカウントに含む
                result_row[goal] = cost
                break
            else:
                if limit >= MAX_ALLOW_COST-1:
                    #limit内にたどり着けなかった駅
                    print member_key, 'は', start, 'から', goal, 'まで規定内コストでたどり着けない！候補から除外します。'
                    result_row[goal] = MAX_DUMMY_COST
                
#ここでresult_rowに入る駅毎のコストのデータは以下のような形になります。（辞書型なので並び順は保証されない）
#{'shinjuku': 4, 'tokyo': 1, 'ikebukuro': 3, 'ueno': 2, 'shibuya': 3, 'shinagawa': 2}
    result[member_key] = result_row
print ''

#ここでresult変数に入る各メンバー毎の各駅へのコストのデータは以下のような形になります。（辞書型なので並び順は保証されない）
#{'A': {'shinjuku': 4, 'tokyo': 1, 'ikebukuro': 3, 'ueno': 2, 'shibuya': 3, 'shinagawa': 2},
# 'B': {'shinjuku': 3, 'tokyo': 2, 'ikebukuro': 4, 'ueno': 3, 'shibuya': 2, 'shinagawa': 1},
# 'C': {'shinjuku': 2, 'tokyo': 3, 'ikebukuro': 1, 'ueno': 2, 'shibuya': 3, 'shinagawa': 4},
# 'D': {'shinjuku': 3, 'tokyo': 2, 'ikebukuro': 2, 'ueno': 1, 'shibuya': 4, 'shinagawa': 3}}
print 'debug文2:各メンバー毎の各駅へのコストのデータのまとめ'
for mem in sorted(result):
   print mem, result[mem] #これはdebug文
#print result
print ''

#全員の各駅へのコストを合算する。
sum_result = {}
del_station_list = []
for member_key in result:
    for station in station_adjacent_dic.keys():
        cost = result[member_key][station]
        if cost == MAX_DUMMY_COST:
            #誰かひとりでもたどり着けない駅であれば探索除外駅
            del_station_list.append(station)
        if sum_result.has_key(station):
            sum_result[station] += cost
        else:
            sum_result[station] = cost

#除外駅をリストから削除する。
for del_station in del_station_list:
    if sum_result.has_key(del_station):
        del sum_result[del_station]

print 'debug文3:全員の各駅へのコストの合算のデータ'
print sum_result
print ''
#ここで各駅のトータルコストのデータは以下のような形となります。
#{'shinjuku': 12, 'tokyo': 8, 'ikebukuro': 10, 'ueno': 8, 'shibuya': 12, 'shinagawa': 10}

cost_dic = {}
for station in sum_result:
   cost = sum_result[station]
   if cost_dic.has_key(cost):
       cost_dic[cost].append(station)
   else:
       cost_dic[cost] = [station] #同じコストが複数駅となることがあるので配列で持つ

print 'debug文4:コスト値をキーに駅を並び替えたデータ'
print cost_dic
print ''
#ここでコスト毎に並び替えた駅の辞書は以下のようなデータになる。
#{8: ['tokyo', 'ueno'], 10: ['ikebukuro', 'shinagawa'], 12: ['shinjuku', 'shibuya']}

if len(cost_dic) == 0:
   print '皆がたどり着ける駅はありませんでした。'
   exit

for idx, cost in enumerate(sorted(cost_dic)):
   if idx == 0:
       print '最もコストの低い駅は、', cost_dic[cost], 'です。'

