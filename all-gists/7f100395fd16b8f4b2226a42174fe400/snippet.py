
# this example shows how you create a dataframe from a list of items in pyspark
# example items ['user_id','cosine']: [('9526756', 1.00000),('314011847', 0.581238)....]

  df=sc.parallelize(items).map(lambda item_:(item_[0],item_[1])).toDF(['user_id','cosine'])
  df.show()

# should print something like:
#+--------+-------------------+
#| user_id|             cosine|
#+--------+-------------------+
#|09526756| 1.00000           |
#|314011847| 0.58123          |
#|55555555| 0.581238          |
#| 2677063| 0.474578          |