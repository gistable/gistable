import multiprocessing
import pandas as pd
import numpy as np

def _apply_df(args):
    df, func, num, kwargs = args
    return num, df.apply(func, **kwargs)

def apply_by_multiprocessing(df,func,**kwargs):
  workers=kwargs.pop('workers')
  pool = multiprocessing.Pool(processes=workers)
  result = pool.map(_apply_df, [(d, func, i, kwargs) for i,d in enumerate(np.array_split(df, workers))])  
  pool.close()
  result=sorted(result,key=lambda x:x[0])
  return pd.concat([i[1] for i in result])

def square(x):
    return x**x
  
if __name__ == '__main__':
    df = pd.DataFrame({'a':range(10), 'b':range(10)})
    apply_by_multiprocessing(df, square, axis=1, workers=4)   