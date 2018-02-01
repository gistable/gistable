# Tweetに含まれる単語のポジネガによる感情度の付与
# 形態要素化できた単語のうち、ポジに分類されるものを1、ネガに分類されるものを-1
# 形態要素化できた単語数で割ることで平均値を取り指標化

pn_data = [data for data in posi_nega_dict.find({},{'word':1,'value':1})]

def get_emotion_value(word):
    ret_val = None
    for d in pn_data:
        if d['word'] == word:
            ret_val = d['value']
            break
    return ret_val

def isexist_and_get_data(data, key):
    return data[key] if key in data else None

data = [d for d in tweetdata.find({'emo_val':{ "$exists": True }},{'noun':1,'adjective':1,'verb':1,'adverb':1})]

tweet_list = []
counter=0
for d in data:
    counter += 1
    if counter % 1000 == 0:
        print counter
        print datetime.datetime.today()
    score = 0
    word_count = 0
    for k in ['noun','adjective','verb','adverb']:
        if type(isexist_and_get_data(d,k))==list:
            for i in d[k]:
                v = get_emotion_value(i)
                if v is not None:
                    score += v
                    word_count += 1
        else:
            v = get_emotion_value(isexist_and_get_data(d,k))
            if v is not None:
                score += v
                word_count += 1
    d['score'] = score/float(word_count) if word_count != 0 else 0
    tweetdata.update({'_id' : d['_id']},{'$set': {'emo_val':d['score']}},True)


