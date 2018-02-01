import pandas as pd
import numpy as np
from sklearn.feature_extraction import DictVectorizer
 
def encode_onehot(df, cols):
    """
    One-hot encoding is applied to columns specified in a pandas DataFrame.
    
    Modified from: https://gist.github.com/kljensen/5452382
    
    Details:
    
    http://en.wikipedia.org/wiki/One-hot
    http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.OneHotEncoder.html
    
    @param df pandas DataFrame
    @param cols a list of columns to encode
    @return a DataFrame with one-hot encoding
    """
    vec = DictVectorizer()
    
    vec_data = pd.DataFrame(vec.fit_transform(df[cols].to_dict(outtype='records')).toarray())
    vec_data.columns = vec.get_feature_names()
    vec_data.index = df.index
    
    df = df.drop(cols, axis=1)
    df = df.join(vec_data)
    return df


def main():
  np.random.seed(42)
  df = pd.DataFrame(np.random.randn(25, 3), columns=['a', 'b', 'c'])

  # Make some random categorical columns
  df['e'] = [random.choice(('Chicago', 'Boston', 'New York')) for i in range(df.shape[0])]
  df['f'] = [random.choice(('Chrome', 'Firefox', 'Opera', "Safari")) for i in range(df.shape[0])]

  # Vectorize the categorical columns: e & f
  df = encode_onehot(df, cols=['e', 'f'])
  print df.head()
 
if __name__ == '__main__':
    main()
