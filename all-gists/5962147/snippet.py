__author__ = 'feng'

articles = [
    'Familiarize Yourself with IntelliJ IDEA editor',
    'While keeping the Ctrl key pressed, rotate the mouse wheel. As you rotate the mouse wheel forward',
    'font size grows larger; as you rotate the mouse wheel backwards, font size decreases',
    'In the popup frame, type Reset font size, and click Enter.',
    'These operations apply to the active editor only. In the other editor tabs, font size is not affected.',
    'There is no default keyboard shortcut associated with Reset font size action. However, you can create your',
    'Place the caret in the editor.'
]

# 给每篇文章编号：id
article_map = dict(zip(range(len(articles)), articles))

# 建立倒排索引
def create_index():
    #  单词到对应的文章id
    # {'word': [1, 2, 3], 'the': [7, 9], 'active': [1]}
    index = {}
    for id, article in article_map.items():
        words = article.split()
        for word in words:
            word = word.lower()
            if word in index:
                index[word].add(id)
            else:
                index[word] = set([id])
    return index


def search_index(query):
    # 切词
    keywords = query.split()
    # 先建立倒排索引。实际中，这个应该时预先建立的
    index = create_index()

    if keywords:
        ids = index.get(keywords[0], set())

        for q in keywords[1:]:
            # 集合的 交 运算
            ids = ids & index.get(q, set())

    for id in ids:
        print article_map[id]


# 直接搜索，需要扫瞄所有的文章。当文章数很多时，有效率问题。
def search(keyword):
    for article in articles:
        if keyword in article:
            yield article


def main():
    search_index("rotate mouse")
    # for result in search('the'):
    #     print re.sub("the", "<b>the</b>", result)
    # print result


if __name__ == "__main__":
    main()