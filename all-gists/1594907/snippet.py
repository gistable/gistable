#a = "(｀･ω･´)"; flatten(a) #=> (´･ω･`) ノ場合

a = "(｀･ω･´)"
def flatten(smiley):
    print smiley.replace("｀","´").replace("´","`")

# >>> flatten(a) #=>(´･ω･`)

# a = "(´･ω･`)"; aodag(a) #=> (´･m･`) ノ場合
b = "(´･ω･`)"

def aodag(smiley):
    print smiley.replace("ω","m")

# >>> aodag(b) #=> (´･m･`)
# あおだぐさんすいません。(´･ω･｀)


# 追加
c = "ヽ(;´Д`)ノ"
def yuruhuwa(smiley):
    print smiley.replace(";´Д`","*´∀｀*")

# >>> yuruhuwa(c) #=>ヽ(*´∀｀*)ノ