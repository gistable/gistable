# -*- coding: utf-8 -*-
# 集合知プログラミング第2章推薦を行う（前半）

# 映画の評者といくつかの映画に対する彼らの評点のディクショナリ
critics = {
			'Lisa Rose':{
						'Lady in the Water': 2.5, 
						'Snakes on a Plane': 3.5, 
						'Just My Luck': 3.0, 
						'Superman Returns': 3.5,
						'You, Me and Dupree': 2.5,
						'The Night Listener': 3.0
						},
			'Gene Seymour':{
						'Lady in the Water': 3.0,
						'Snakes on a Plane': 3.5,
						'Just My Luck': 1.5, 
						'Superman Returns': 5.0,
						'The Night Listener': 3.0,
						'You, Me and Dupree': 3.5
						},
			'Michael Phillips':{
						'Lady in the Water': 2.5,
						'Snakes on a Plane': 3.0,
						'Superman Returns': 3.5,
						'The Night Listener': 4.0
						},
			'Claudia Puig':{
						'Snakes on a Plane': 3.5, 
						'Just My Luck': 3.0, 
						'The Night Listener': 4.5, 
						'Superman Returns': 4.0, 
						'You, Me and Dupree': 2.5
						},
			'Mick LaSalle':{
						'Lady in the Water': 3.0,
						'Snakes on a Plane': 4.0,
						'Just My Luck': 2.0, 
						'Superman Returns': 3.0,
						'The Night Listener': 3.0,
						'You, Me and Dupree': 2.0
						},
			'Jack Matthews':{
						'Lady in the Water': 3.0,
						'Snakes on a Plane': 4.0,
						'The Night Listener': 3.0,
						'Superman Returns': 5.0,
						'You, Me and Dupree': 3.5
						},
			'Toby':{
						'Snakes on a Plane': 4.5,
						'You, Me and Dupree': 1.0,
						'Superman Returns': 4.0
						}
			}

"""
pythonを以下実行。データを検索
>> critics['Lisa Rose']['Lady in the Water']
出力結果
2.5

pythonを以下実行。データを変更する
>> critics['Toby']['Snakes on a Plane']=4.0
>> critics['Toby']
出力結果
{'Snakes on a Plane': 4.5, 'Superman Returns': 4.0, 'You, Me and Dupree': 1.0}
"""

from math import sqrt

# ユークリッド距離によるスコア
# person1とperson2の距離をもとにした類似性スコアを返す
def sim_distance(prefs, person1,person2):
	# 二人とも評価しているアイテムのリストを得る
	si={}
	for item in prefs[person1]:
		if item in prefs[person2]:
			si[item]=1

	# 両者共に評価しているものが一つもなければ0を返す
	if len(si)==0: return 0

	# すべての差の平方を足し合わせる
	sum_of_squares=sum([pow(prefs[person1][item]-prefs[person2][item],2)
						for item in prefs[person1] if item in prefs[person2]])

	# 本ではsqrtがない(誤植)がここは逆数にする必要があるので、sqrtを追記
	return 1/(1+sqrt(sum_of_squares))

"""
pythonインタプリタで以下を実行。二人の名前と一書に呼び出すことで類似スコアを得ることができる
>> recommendations.sim_distance(recommendations.critics,'Lisa Rose','Gene Seymour')
出力結果
0.29429805508554946
"""

# ピアソン相関によるスコア
# p1とp2のピアソン相関係数を返す
def sim_pearson(prefs,p1,p2):
	# 両者が互いに評価しているアイテムのリストを取得
	si={}
	for item in prefs[p1]:
		if item in prefs[p2]: si[item]=1

	# 要素の数を調べる
	n=len(si)

	# 共に評価しているアイテムがなければ0を返す
	if n==0: return 0

	# すべれの嗜好を合計する
	sum1=sum([prefs[p1][it] for it in si])
	sum2=sum([prefs[p2][it] for it in si])

	# 平方を合計する
	sum1Sq=sum([pow(prefs[p1][it], 2) for it in si])
	sum2Sq=sum([pow(prefs[p2][it], 2) for it in si]) 

	# 積を合計する
	pSum=sum([prefs[p1][it] * prefs[p2][it] for it in si])

	# ピアソンによるスコアを計算する
	num=pSum-(sum1*sum2/n)
	den=sqrt((sum1Sq-pow(sum1, 2)/n)*(sum2Sq-pow(sum2, 2)/n))
	if den==0: return 0

	r=num/den

	return r

"""
pythonインタプリタで以下を実行。二人の名前と一書に呼び出すことで類似スコアを得ることができる
>> print recommendations.sim_pearson(recommendations.critics, 'Lisa Rose', 'Gene Seymour')
出力結果
0.396059017191
"""

# 評者をランキングする
# ディクショナリprefsとpersonにもっともマッチするものたちを返す
# 結果の数と類似性関数はオプションのパラメータ
def topMatches(prefs, person, n=5, similarity=sim_pearson):
	scores=[(similarity(prefs,person,other),other)
			for other in prefs if other!=person]

	# 高スコアがリストの最初に来るように並び替える
	scores.sort()
	scores.reverse()
	return scores[0:n] 

"""
pythonで以下を実行。自分と自分以外のすべてのユーザを比較し、ソートされた結果から最初のn個の結果を返す
>> recommendations.topMatches(recommendations.critics,'Toby',n=3)
出力結果
[(0.99124070716192991, 'Lisa Rose'),
 (0.92447345164190486, 'Mick LaSalle'),
 (0.89340514744156474, 'Claudia Puig')]
おまけでユークリッド距離でランキングを出すと以下の結果になる
[(0.40000000000000002, 'Mick LaSalle'),
 (0.38742588672279304, 'Michael Phillips'),
 (0.35678917232533092, 'Claudia Puig')]
"""

# アイテムを推薦する
# person以外の全てのユーザの評点の重み付き平均を使い、personへの推薦を算出する
def getRecommendations(prefs,person,similarity=sim_pearson):
	totals={}
	simSums={}
	for other in prefs:
		# 自分自身とは比較しない
		if other==person: continue
		sim=similarity(prefs,person,other)

		if sim<=0: continue

		for item in prefs[other]:
			# まだみていない映画の特典のみを算出
			if item not in prefs[person] or prefs[person][item]==0:
				# 類似度 * スコア
				totals.setdefault(item,0)
				totals[item]+=prefs[other][item]*sim
				# 類似度計算
				simSums.setdefault(item,0)
				simSums[item]+=sim
	# 正規化したリストを作る
	rankings=[(total/simSums[item],item) for item,total in totals.items()]

	# ソート済みのリストを作る
	rankings.sort()
	rankings.reverse()
	return rankings

"""
pythonで以下実行。自分が観るべき映画を知ることができる
>> recommendations.getRecommendations(recommendations.critics,'Toby')
出力結果
[(3.3477895267131013, 'The Night Listener'),
 (2.8325499182641614, 'Lady in the Water'),
 (2.5309807037655645, 'Just My Luck')]

pythonで以下実行。ユークリッド距離で計算
>> recommendations.getRecommendations(recommendations.critics,'Toby',similarity=recommendations.sim_distance)
出力結果
[(3.457128694491423, 'The Night Listener'),
 (2.7785840038149239, 'Lady in the Water'),
 (2.4224820423619167, 'Just My Luck')]
"""

# 似ている製品
def trasformPrefs(prefs):
	result={}
	for person in prefs:
		for item in prefs[person]:
			result.setdefault(item,{})

			# itemとpersonを入れ替える
			result[item][person]=prefs[person][item]
	return result

"""
pythonで以下実行。関数topMatchesを呼び出しSuperman Returnsに似ている映画を探す
>> movies=recommendations.trasformPrefs(recommendations.critics)
>> recommendations.topMatches(movies,'Superman Returns')
出力結果
[(0.65795169495976946, 'You, Me and Dupree'),
 (0.48795003647426888, 'Lady in the Water'),
 (0.11180339887498941, 'Snakes on a Plane'),
 (-0.17984719479905439, 'The Night Listener'),
 (-0.42289003161103106, 'Just My Luck')]

pythonで以下実行。映画の評者を推薦してもらう
>> recommendations.getRecommendations(movies,'Just My Luck')
出力結果
Out[22]: [(4.0, 'Michael Phillips'), (3.0, 'Jack Matthews')]
"""
