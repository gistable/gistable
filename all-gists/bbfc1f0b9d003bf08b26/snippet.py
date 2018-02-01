import numpy as np
import pandas as pd
from lxml import html
from sklearn import metrics
from sklearn.cross_validation import train_test_split
from sklearn.linear_model import LogisticRegression as LR
from sklearn.feature_extraction.text import TfidfVectorizer

def clean(text):
	return html.fromstring(text).text_content().lower().strip()

tr_data = pd.read_csv('/media/datasets/kaggle_imdb/labeledTrainData.tsv', delimiter='\t')
te_data = pd.read_csv('/media/datasets/kaggle_imdb/testData.tsv', delimiter='\t')

trX = [clean(text) for text in tr_data['review'].values]
trY = tr_data['sentiment'].values

vect = TfidfVectorizer(min_df=10, ngram_range=(1, 2))
trX = vect.fit_transform(trX)

model = LR()
model.fit(trX, trY)

ids = te_data['id'].values
teX = [clean(text) for text in te_data['review'].values]
teX = vect.transform(teX)
pr_teX = model.predict_proba(teX)[:, 1]

pd.DataFrame(np.asarray([ids, pr_teX]).T).to_csv('test.csv',index=False,header=["id", "sentiment"])