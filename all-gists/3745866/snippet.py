>>> from pandas import DataFrame
>>> from sklearn.feature_extraction.text import CountVectorizer
>>> docs = ["You can catch more flies with honey than you can with vinegar.",
...         "You can lead a horse to water, but you can't make him drink."]
>>> vect = CountVectorizer(min_df=0., max_df=1.0)
>>> X = vect.fit_transform(docs)
>>> print(DataFrame(X.A, columns=vect.get_feature_names()).to_string())
   but  can  catch  drink  flies  him  honey  horse  lead  make  more  than  to  vinegar  water  with  you
0    0    2      1      0      1    0      1      0     0     0     1     1   0        1      0     2    2
1    1    2      0      1      0    1      0      1     1     1     0     0   1        0      1     0    2