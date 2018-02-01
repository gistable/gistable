"""making a dataframe"""
df = pd.DataFrame([[1, 2], [3, 4]], columns=list('AB'))

"""quick way to create an interesting data frame to try things out""" 
df = pd.DataFrame(np.random.randn(5, 4), columns=['a', 'b', 'c', 'd'])

"""convert a dictionary into a DataFrame"""
"""make the keys into columns"""
df = pd.DataFrame(dic, index=[0])

"""make the keys into row index""" 
df = pd.DataFrame.from_dict(dic, orient='index')

"""append two dfs"""
df.append(df2, ignore_index=True)

"""concat many dfs"""
pd.concat([pd.DataFrame([i], columns=['A']) for i in range(5)], ignore_index=True)

df['A'] """ will bring out a col """ df.ix[0] """will bring out a row, #0 in this case""" 

"""to get an array from a data frame or a series use values, note it is not a function here, so no parans ()"""
point = df_allpoints[df_allpoints['names'] == given_point] # extract one point row. 
point = point['desc'].values[0] # get its descriptor in array form. 


"""Given a dataframe df to filter by a series s:""" 
df[df['col_name'].isin(s)]

"""to do the same filter on the index instead of arbitrary column"""
df.ix[s]

""" display only certain columns, note it is a list inside the parans """
df[['A', 'B']]

"""drop rows with atleast one null value, pass params to modify 
to atmost instead of atleast etc.""" 
df.dropna()

"""deleting a column""" 
del df['column-name'] # note that df.column-name won't work. 

"""making rows out of whole objects instead of parsing them into seperate columns"""
# Create the dataset (no data or just the indexes)
dataset = pandas.DataFrame(index=names)

# Add a column to the dataset where each column entry is a 1-D array and each row of “svd” is applied to a different DataFrame row
dataset['Norm']=svds

"""sort by value in a column"""
df.sort_values('col_name')

"""filter by multiple conditions in a dataframe df
   parentheses!""" 
df[(df['gender'] == 'M') & (df['cc_iso'] == 'US')]

"""filter by conditions and the condition on row labels(index)"""
df[(df.a > 0) & (df.index.isin([0, 2, 4]))]

"""regexp filters on strings (vectorized), use .* instead of *"""
df[df.category.str.contains(r'some.regex.*pattern')]

"""logical NOT is like this"""
df[~df.category.str.contains(r'some.regex.*pattern')]

"""creating complex filters using functions on rows: http://goo.gl/r57b1"""
df[df.apply(lambda x: x['b'] > x['c'], axis=1)]

"""Pandas replace operation http://goo.gl/DJphs"""
df[2].replace(4, 17, inplace=True)
df[1][df[1] == 4] = 19

"""apply and map examples"""
"""add 1 to every element"""
df.applymap(lambda x: x+1)

"""add 2 to row 3 and return the series"""
df.apply(lambda x: x[3]+2,axis=0)

"""add 3 to col A and return the series"""
df.apply(lambda x: x['a']+1,axis=1)


"""assigning some value to a slice is tricky as sometimes a copy is returned, 
sometimes a view is returned based on numpy rules, more here:
http://pandas.pydata.org/pandas-docs/stable/indexing.html#indexing-advanced"""
df.ix[df['part'].isin(ids), 'assigned_name']  =  "some new value"

"""example of applying a complex external function 
to each row of a data frame""" 
def stripper(x):
    l = re.findall(r'[0-9]+(?:\.[0-9]+){3}', x['Text with IP adress embedded'])
    # you can take care of special 
    # cases and missing values, more than expected 
    # number of return values etc like this. 
    if l == []:
        return ''
    else: 
        return l[0]

df.apply(stripper, axis=1)

"""can pass extra args and named ones eg..""" 
def subtract_and_divide(x, sub, divide=1):
    return (x - sub) / divide
    
"""You may then apply this function as follows:"""
df.apply(subtract_and_divide, args=(5,), divide=3)

"""sort a groupby object by the size of the groups""" 
dfl = sorted(dfg, key=lambda x: len(x[1]), reverse=True)

"""compute the means by group, and save mean to every element so group mean is available for every sample"""
sil_means = df.groupby('labels').mean()
df = df.join(sil_means, on='labels',  rsuffix='_mean')

"""groupby used like a histogram to obtain counts on sub-ranges of a variable, pretty handy""" 
df.groupby(pd.cut(df.age, range(0, 130, 10))).size()

"""finding the distribution based on quantiles""" 
df.groupby(pd.qcut(df.age, [0, 0.99, 1])

"""if you don't need specific bins like above, and just want to count number of each values"""
df.age.value_counts()

"""one liner to normalize a data frame""" 
(df - df.mean()) / (df.max() - df.min())

"""iterating and working with groups is easy when you realize each group is itself a DataFrame""" 
for name, group in dg:
    print name, print(type(group))

"""grouping and applying a group specific function to each group element, 
I think this could be simpler, but here is my current version""" 
quantile = [0, 0.50, 0.75, 0.90, 0.95, 0.99, 1]
grouped = df.groupby(pd.qcut(df.age, quantile))
frame_list = []
for i, group in enumerate(grouped):
   (label, frame) = group
   frame['age_quantile'] = quantile[i + 1]
   frame_list.append(frame)
df = pd.concat(frame_list)

"""misc: set display width, col_width etc for interactive pandas session""" 
pd.set_option('display.width', 200)
pd.set_option('display.max_colwidth', 20)
pd.set_option('display.max_rows', 100)
           
