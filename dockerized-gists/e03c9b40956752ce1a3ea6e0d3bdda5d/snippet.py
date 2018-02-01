
# coding: utf-8

# # MonkeyBench : an interactive environment for library research
# 
# 
# MonkeyBenchは、Jupyterの上に構築中のライブラリーリサーチのための対話環境です。
# 
# ライブラリーリサーチの過程と成果を、そのためのツールの作成と利用込みで、そのまま保存／共有／再利用できるという利点を活かし、調査プロセスの振り返りから質の向上、ノウハウ化を支援する環境となることを目論んでいます。
# 
# ノイラートの船ではありませんが、「使いながら作り続ける」というコンセプトのため、完成することはありませんが、ツールの寄せ集めという性質上、それぞれ一部分でも利用可能なので、公開してみました。

# # コマンド一覧とワークフロー
# 
# ## 予備調査
# 
# | マジックコマンド | 機能 | 
# |:-----------|:------------|
# | %dictj （キーワード）　 | 　キーワードについて手持ちの辞書(EPWING）とネット上の日本語事典をまとめて検索し、記述の短い順から並べて表示 |
# | %refcase （キーワード） |　レファレンス共同データベースを検索して、レファレンス事例を収集して表示 |
# | %thememap （キーワード） |　キーワードについてウィキペディアのカテゴリー情報を元に、該当する分野の階層図を作成する |
# | %suggestmap （キーワード） |　キーワードについてgoogleサジェスト機能を使って、検索で共に使われる共起語を集めてマップ化する |
# | %kotobankmap （キーワード） |　kotobankの関連キーワードをつかって関連図をつくる |
# | %webliomap （キーワード） |　weblioの関連キーワードをつかって関連図をつくる |
# 
# ## 文献調査
# 
# | マジックコマンド | 機能 | 
# |:-----------|:------------|
# |%webcat （キーワード）| 　webcat plus minusを使って書籍等を検索して、結果をデータフレームにする|
# | %ndl  （キーワード）|　国会図書館サーチを検索して、結果をデータフレームにする<br>書籍、雑誌記事だけでなく、デジタル資料やレファレンス事例などを含めて検索できるが、上限５００件の制限がある|
# |%amazonsimi （キーワード）|　アマゾンの類似商品情報を辿って、関連書を集める|
# |%amazonmap （キーワード）|　アマゾンの類似商品情報を辿って集めた関連書を、関連チャートに図化する|
# |%amazonPmap （キーワード）|　アマゾンの類似商品情報を辿って集めた関連書を、商品写真を使って関連チャートに図化する|
# 
# 
# ## 文献調査補助
# 
# | マジックコマンド | 機能 | 
# |:-----------|:------------|
# | %extbook （データフレーム）|  　データフレーム内に含まれる書名を抜き出してデータフレーム化する<br>　事典検索やレファレンス事例の結果から書名を抜き出すのに用いる| 
# |  %%text2bib <br>（複数行の書誌データ）| テキストから書誌情報を拾ってデータフレーム化する<br>　コピペや手入力で文献を入力するのに用いる| 
# |  %makebib （データフレーム）（データフレーム）……| 　文献調査の各コマンドが出力した複数のデータフレームをマージして重複を除き、詳細情報を取得してデータフレーム化する| 
# |%amazonreviews （書誌データフレーム）|データフレーム内に含まれる目次情報を展開する|
# |%amazonreviews （書誌データフレーム）|データフレーム内に含まれる書籍についてamazonレビューを収集する|
# 
# ## 所在調査
# 
# | マジックコマンド | 機能 | 
# |:-----------|:------------|
# | %librarylist （地名、駅名など）| 　地名、駅名など（コンマ区切りで複数指定可能）を入力すると、該当する／付近の図書館のリストをデータフレームにする<br>次の％librarystatueで検索対象図書館を指定するのに使う| 
# | ％librarystatue （書誌データフレーム）（図書館リストデータフレーム）| 　書誌データフレームと図書館リストデータフレームを受けて、各書籍について各図書館の所蔵／貸出情報／予約用URLを取得してデータフレームする| 
# | %stock_amazon （書誌データフレーム）| 　書誌データフレームを受けて、各書籍についてAmazonの在庫、新刊・中古の最低価格を取得してデータフレームする| 
# |  %stock_kosho （書誌データフレーム）| 　書誌データフレームを受けて、各書籍について「日本の古本屋」の在庫、出品店・価格等を取得してデータフレームする| 
# | %stock_ndl  （書誌データフレーム）| 　書誌データフレームを受けて、各書籍について国会図書館、各県立図書館の所蔵／貸出情報／予約用URLを取得してデータフレームする| 
# 
# 
# 
# <img src="http://blog-imgs-90.fc2.com/r/e/a/readingmonkey/MonkeyBench.png">

# # コード

# In[1]:


import urllib2
import requests
import lxml.html
from bs4 import BeautifulSoup
import pandas as pd
from collections import OrderedDict
import re
from IPython.display import HTML
from IPython.core.magic import (register_line_magic, register_cell_magic)
from StringIO import StringIO
import pygraphviz as pgv
import cStringIO


# In[2]:

#key関係
AMAZON_ACCESS_KEY_ID="XXXXXXXXXXXXXXXXXXXX"
AMAZON_SECRET_KEY="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx+x+xxxxx"
AMAZON_ASSOC_TAG="xxxxxxxxxxxxx-99"

calil_app_key = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'


# In[3]:

#自分の行きつけの図書館
my_lib_string='''
systemid,systemname,formal,address,tel,geocode,category,url_pc
Osaka_Osaka,大阪府大阪市,大阪市立中央図書館,大阪府大阪市西区北堀江4-3-2,06-6539-3300,"135.486381,34.673879",MEDIUM,http://www.oml.city.osaka.lg.jp/
'''
sio = StringIO(my_lib_string)
MYLIBRARY = pd.read_csv(sio)


# ## 汎用ツール系

# In[4]:

#結果の表示援助
def pp(df, now_index, now_column='description'):
    if now_column == 'url':
        return HTML(df[now_column][now_index])
    else:
        return HTML(df[now_column][now_index].replace('\n','<br>'))

def url(df, now_index):
    if 'url' in df.columns:
        return HTML(df['url'][now_index])

def p(df):
    for now_column in df.columns:
        print now_column + '\t',
    print
    print ' --- '
    datanum, fieldnum = df.shape
    for i in range(0, datanum):
        for now_column in df.columns:
            print unicode(df[now_column].iat[i]).strip().encode('utf-8')+ '\t',
        print
        print ' --- '

#データフレームをHTML埋め込み
def embed_df(df):
    datanum, fieldnum = df.shape
    now_html = '<table><th></th>'
    for now_column in df.columns:
        now_html += '<th>' +unicode(now_column)+'</th>'
    for i in range(0, datanum):
        now_html +='<tr><th>{}</th>'.format(i+1)
        for now_column in df.columns:
            now_item = df[now_column].iat[i]
            #print now_item, type(now_item)
            if 'url' in now_column and 'http' in unicode(now_item):
                now_html += u'<td><a href="{0}" target="_blank">LINK</a></td>'.format(now_item)
            else:
                now_html += u'<td>' +unicode(now_item) +u'</td>'
        now_html +='</tr>'
    now_html +='</table>'
    return HTML(now_html)

@register_cell_magic
def csv2df(line, cell):
    # We create a string buffer containing the
    # contents of the cell.
    sio = StringIO(cell)
    # We use pandas' read_csv function to parse
    # the CSV string.
    return pd.read_csv(sio)


# In[5]:

#『書名』を切り出してリストで返す
def extract_titles_from_text(text, recom):
    r = re.compile(recom)
    text = unicode(text)
    books= r.findall(text)
    if books:
        return books
    else:
        return None

def extract_book_titles_from_text(text):
    r = re.compile(u'『([^』]+)』')
    text = unicode(text)
    books= r.findall(text)
    if books:
        return books
    else:
        return None

def extract_engbook_titles_from_text(text):
    r = re.compile(r'<em>([A-Z][^<]+)</em>')
    text = unicode(text)
    books= r.findall(text)
    if books:
        return books
    else:
        return None

def extract_eng_article_titles_from_text(text):
    r = re.compile(u'“([A-Z][^”]+),”')
    text = unicode(text)
    books= r.findall(text)
    if books:
        return books
    else:
        return None



# データフレームから『書名』を抜き出す
def extract_titles_from_df(df, recom):
    result_list = []
    datanum, fieldnum = df.shape
    for i in range( datanum):
        for j in range(fieldnum):
            title_list = extract_titles_from_text(df.iloc[i,j],recom)
            if title_list:
                for title in title_list:
                    if title not in result_list:
                        result_list.append(title)
    return result_list


def ext_book(df):
    result_df = pd.DataFrame(columns =['title'])
    extract_method = {'本':u'『([^』]+)』','Book':r'<em>([A-Z][^<]+)</em>', 'Article':u'“([A-Z][^”]+),”'}
    for category, recom in extract_method.items():
        for now_title in extract_titles_from_df(df, recom):
            result_dict = OrderedDict()
            result_dict['category'] = category,
            result_dict['title'] = now_title,
            result_df = result_df.append(pd.DataFrame(result_dict))
    result_df.index = range(1, len(result_df)+1) #最後にインデックスつけ
    return result_df


# In[6]:

def ext_amazon(url):
    '''
    urlで指定されるページからamazon.co.jpへのリンクを抽出してtitle, asinのデータフレームを返す
    '''
    r = requests.get(url)
    soup = BeautifulSoup(r.text.encode(r.encoding),'lxml')
    amazon_items = soup.findAll('a', {'href':re.compile(r'http://www.amazon.co.jp.+')})
    result_dict = OrderedDict()
    result_dict['title'] = [a.text for a in amazon_items]
    result_dict['asin'] = [re.search(r'[0-9X]{10,10}',a.attrs['href']).group() for a in amazon_items]
    return pd.DataFrame(result_dict)


# ## Amazon関係

# In[7]:

from bottlenose import api
from urllib2 import HTTPError


amazon = api.Amazon(AMAZON_ACCESS_KEY_ID, AMAZON_SECRET_KEY, AMAZON_ASSOC_TAG, Region="JP")

def error_handler(err):
  ex = err['exception']
  if isinstance(ex, HTTPError) and ex.code == 503:
    time.sleep(random.expovariate(0.1))
    return True


def get_totalpages(keywords, search_index="All"):
    response = amazon.ItemSearch(
             SearchIndex=search_index,
             Keywords=keywords,
             ResponseGroup="ItemIds",
             ErrorHandler=error_handler)
    soup=BeautifulSoup(response, "lxml")
    # print soup
    totalpages=int(soup.find('totalpages').text)
    return totalpages

def item_search(keywords, search_index="All", item_page=1):
    try:
        response = amazon.ItemSearch(
            SearchIndex=search_index, 
            Keywords=keywords, 
            ItemPage=item_page, 
            ResponseGroup="Large",
            ErrorHandler=error_handler)
        # バイト配列をunicodeの文字列に
        # コレをしないと日本語は文字化けします。
        u_response = response.decode('utf-8','strict')
        soup = BeautifulSoup(u_response, "lxml")
        return soup.findAll('item')
    except:
        return None

def item_title_book_search(title, search_index="Books", item_page=1):
    try:
        response = amazon.ItemSearch(
            SearchIndex=search_index, 
            Title=title, 
            ItemPage=item_page, 
            ResponseGroup="Large",
            ErrorHandler=error_handler)
        # バイト配列をunicodeの文字列に
        # コレをしないと日本語は文字化けします。
        u_response = response.decode('utf-8','strict')
        soup = BeautifulSoup(u_response, "lxml")
        return soup.findAll('item')
    except:
        return None


# ## 文献調査

# In[8]:

class Searcher(object):    
    """
    抽象クラス　複数のリソースを始めとする調べて結果を合わせて並べ替えて出力
    入力ーキーワード self.keyword
    出力ーデータフレーム（項目名、リソース名、内容、記述量など）
    クラスプロパティ resource_dict={name : path  } リソースのリスト＝リソース名とアクセス情報（URLや辞書をのパスなど）
    """
    #クラスプロパティ
    #リソースのリスト＝リソース名とアクセス情報（URLや辞書をのパスなど）
    resource_dict={}
    
    def __init__(self, keyword):
        self.keyword = keyword
    
    def collector(self):
        result_df = pd.DataFrame () #入れ物を用意する
        resource_list = self.make_resource_list()
        #print len(resource_list), 'Loops'
        for resource in resource_list:  #リソースリストから一つずつ取り出すループ
            print '.',
            result_df = result_df.append( self.fetch_data(resource)  ) #キーワードについてそのリソースからデータを得て、入れ物に追加
        result_df = self.arrange(result_df) #ループ終わったら入れ物の中身をソート
        return result_df  #入れ物の中身を返す


# ## 辞書集め(epwing)

# In[9]:

import commands
class epwing_info(Searcher):
    dict_root = '/Users/kuru/Documents/EPWING/'
    resource_dict={
        'ブリタニカ小項目版' : ['ブリタニカ国際大百科事典.Windows対応小項目版.2000','-t+'],
        'マグローヒル科学技術用語大辞典' : ['マグローヒル科学技術用語大辞典.第3版','-t+'],
        '医学大辞典' : ['医歯薬\ 医学大辞典','-t+'],
        '岩波日本史辞典' : ['岩波\ 日本史辞典-ebzip','-t+'],
        '理化学辞典第五版ebzip' : ['岩波\ 理化学辞典第五版ebzip','-t+'],
        '広辞苑' : ['岩波.広辞苑.第六版','-t+'],
        '岩波ケンブリッジ世界人名辞典' : ['岩波\=ケンブリッジ世界人名辞典ebzip','-t+'],
        '岩波生物学辞典' : ['岩波生物学辞典第四版','-t+'],
        '建築事典' : ['建築事典ebzip','-t+'],
        'リーダーズ' : ['研究社\ リーダーズプラス\ V2ebzip','-t+'],
        '大辞林' : ['三省堂大辞林','-t+'],
        '参考図書2.4万冊' : ['参考図書2.4万冊','-t+'],
        '参考調査便覧' : ['参考調査便覧epwing','-tmax'],
        '国語大辞典' : ['小学館\ 国語大辞典ebzip','-t+'],
        '日本大百科全書' : ['小学館\ 日本大百科全書ebzip','-t+'],
        'ランダムハウス英語辞典' : ['小学館.ランダムハウス英語辞典','-t+'],
        '大辞泉' : ['小学館.大辞泉','-t+'],
        '心理学用語辞典' : ['心理学用語辞典','-t+'],
        '人物レファレンス事典' : ['人物レファレンス事典\ 日本編-ebzip','-t+'],
        '南山堂医学大辞典' : ['南山堂医学大辞典第18版','-t+'],
        '科学技術45万語対訳辞典' : ['日外アソシエーツ\ 科学技術45万語対訳辞典\ 英和／和英','-t+'],
        '物語要素事典' : ['物語要素事典epwing','-t+'],
        '世界大百科事典' : ['平凡社\ 世界大百科事典\ 第二版','-t+'],
        '有斐閣経済辞典' : ['有斐閣-経済辞典-第3版-ebzip','-t+']} 
    
    def make_resource_list(self):
        return self.resource_dict.keys()
    
    def make_query(self, resource_name):
        dict_info = self.resource_dict[resource_name]
        path = self.dict_root + dict_info[0]
        search_mode = dict_info[1]
        return 'ebmini -b{dict_path} -KIu -KOu -n1 {mode} -l- -s{keyword}'.format(dict_path=path, mode=search_mode, keyword=self.keyword)
        
    def fetch_data(self, resource_name):
        result = commands.getoutput(self.make_query(resource_name) )
        result_dict = OrderedDict()
        result_dict['item_title'] = result.split('\n')[0].decode('utf-8'),
        result_dict['dict_name'] = resource_name.decode('utf-8'),
        result_dict['description'] = result.decode('utf-8'),
        result_dict['des_size'] = len(result),
        return pd.DataFrame(result_dict)
 
    def arrange(self, df):
        if not df.empty:
            df = df[df.des_size >0] #長さゼロは抜く
            df = df[df.item_title !='Error: eb_bind() failed.'] #失敗は抜く
            df = df.sort_values(by='des_size') #並べ替え
            df.index = range(1, len(df)+1) #最後にインデックスつけ
        return df



# ## コトバンク

# In[10]:

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}

    
class Kotobank_info(Searcher):
    
    def make_resource_list(self):
        '''
        yahoo辞書でキーワードを拾い直して、それらのキーワードそれぞれにURLを作って、リストで返す
        '''
        url = 'http://dic.search.yahoo.co.jp/search?p=' + self.keyword + '&stype=exact&aq=-1&oq=&ei=UTF-8'
        content = requests.get(url,  headers=headers).text
        soup = BeautifulSoup(content, "lxml") 
        #<h3><a href="・・・・">駄洒落</a></h3>
        url_list = []
        h3_soups = soup.findAll('h3')
        if h3_soups:
            for h3_soup in h3_soups:
                url = 'https://kotobank.jp/word/' + urllib2.quote(h3_soup.text.encode('utf-8'))
                if url not in url_list:
                    url_list.append(url)
        return url_list
    
    def fetch_data(self, url):
        '''
        URLを開いてパースして拾い出す
        '''
        content = requests.get(url,  headers=headers).text
        
        soup = BeautifulSoup(content, "lxml") 
        article_soups = soup.findAll('article')
        result_df = pd.DataFrame()

        if article_soups:
            #ダイレクトで見つかった場合
            for article_soup in article_soups:

                # <h2>◯◯辞典<span>の解説</span></h2>を見つけて
                dict_name = article_soup.find('h2').text
                dict_name = dict_name.replace(u'の解説','')

                # <h3>項目/h3>を見つけて
                item_title_soup = article_soup.find('h3')
                item_title = item_title_soup.text.replace('\n','').strip()

                # <section class=description>を見つけて
                description_soup = article_soup.find('section', class_='description')
                description = description_soup.text
                description = description.replace('\t','').strip()
                description = description.replace('\n','').strip()
                description = description.replace(' ','').strip()
                
                result_dict = OrderedDict()
                result_dict['item_title'] = item_title,
                result_dict['dict_name'] = dict_name,
                result_dict['description'] = description,
                result_dict['des_size'] = len(description),
                result_dict['url'] = url,

                newdf = pd.DataFrame(result_dict)
                result_df = result_df.append(newdf)
            return result_df
        else:
            return None
        
 
    def arrange(self, df):
        #print df
        if not df.empty:
            df = df[df.des_size >0] #長さゼロは抜く
            df = df.sort_values(by='des_size') #並べ替え
            df.index = range(1, len(df)+1) #最後にインデックスつけ
        return df


# ## Weblio

# In[11]:

def weblio(keyword):
    #keyword = 'ニューラルネットワーク'
    url = 'http://www.weblio.jp/content/'+keyword
    r = requests.get( url)
    tree = lxml.html.fromstring(r.content)
    # links = tree.xpath('//div[@class="pbarTL"]') #辞書名
    #links = tree.xpath('//div[@class="NetDicHead"]') #項目名のタグは辞書ごとに違うみたい
    # links = tree.xpath('//h2[@class="midashigo"]' )#各辞書の見出し
    # links = tree.xpath('//div[@class="sideRWordsL"]/a') #関連語
    links = tree.xpath('//*[@id="topicWrp"]/span' ) #全体の見出し
    for link in links:
        print link.text_content()
        print link.attrib['href']


# ## Encyclopedia.com

# In[12]:

def myjoin(list):
    result = ''
    for i in list:
        result += unicode(i)
    return result

class encyclopediacom_info(Searcher):
    
    def make_resource_list(self):
        url = 'http://www.encyclopedia.com/searchresults.aspx?q=' + self.keyword
        content = requests.get(url,  headers=headers).text
        soup = BeautifulSoup(content, "lxml") 
        #<a class="maltlink" href="/topic/encyclopedia.aspx" onclick="OmnitureClick('SearchResults20008.topiclink');">encyclopedia</a>
        maltlink_soup = soup.find('a', class_='maltlink')
        if maltlink_soup:
            url_list = 'http://www.encyclopedia.com' + dict(maltlink_soup.attrs)['href'],
        return url_list
    
    def fetch_data(self, url):
        '''
        URLを開いてパースして拾い出す
        '''
#         driver = webdriver.PhantomJS()
#         driver.get(url)
#         r = driver.page_source

        r = requests.get(url)
        soup = BeautifulSoup(r.text,"lxml")
        
        article_titles = soup.findAll('h2', class_ ='doctitle')
        source_titles = soup.findAll('span', class_='pub-name')
        be_doc_texts = soup.findAll('div', id='be-doc-text')
        APA_citations = soup.findAll('div', id='divAPA')
        
        df = pd.DataFrame()
        for article_title, source_title, doc_text, apa in zip(article_titles, source_titles, be_doc_texts, APA_citations):
            result_dict = OrderedDict()
            result_dict['item_title'] = article_title.text, 
            result_dict['dict_name'] = source_title.text,
            #result_dict['description'] = doc_text.text,
            result_dict['description'] = myjoin(doc_text.contents),
            #result_dict['citation']  = apa.find('p', class_='cittext').text,
            result_dict['citation']  = myjoin(apa.find('p', class_='cittext')),
            result_dict['des_size'] = len(doc_text.text),
            df = df.append(pd.DataFrame(result_dict))
    
        return df
 
    def arrange(self, df):
        if not df.empty:
            df = df[df.des_size >0] #長さゼロは抜く
            df = df.sort_values(by='des_size') #並べ替え
            df.index = range(1, len(df)+1) #最後にインデックスつけ
        return df


# ## Wikipedias

# In[13]:

class Wikipedia_Info(object):
    
    def __init__(self, keyword, language='en'):
        self.keyword = keyword
        self.language = language
        
    def fetch_page(self):
        import wikipedia
        wikipedia.set_lang(self.language)
        language_dict = wikipedia.languages()
        try:
            page = wikipedia.WikipediaPage(self.keyword)
            result_dict = OrderedDict()
            result_dict['item_title'] = unicode(page.original_title),
            result_dict['dict_name'] = u'Wikipedia ' + language_dict[self.language],
            result_dict['description'] = page.content,
            result_dict['des_size'] = len(page.content),
            result_dict['url'] = page.url,
            wiki_df = pd.DataFrame(result_dict)
            return wiki_df
        except:
            print u'Page  {} does not match any pages in {} '.format(self.keyword, u'Wikipedia ' + language_dict[self.language])
        


# In[14]:

def interlanguage(keyword):
    url = "https://ja.wikipedia.org/wiki/" + keyword
    print url
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text.encode('utf-8'),"lxml")

    result_dict = OrderedDict()
    
    # <li class="interlanguage-link interwiki-ab">
    # <a href="//ab.wikipedia.org/wiki/%D0%90%D0%BB%D0%B0" title="アブハズ語: Ала" lang="ab" hreflang="ab">Аҧсшәа</a>
    # </li>

    interlanguage_link_soups = soup.findAll("li", class_=re.compile(r'interlanguage.+'))
    #print interlanguage_link_soups
    if interlanguage_link_soups:
        result_dict['word'] = [dict(l.a.attrs)['title'].split(': ')[1] for l in interlanguage_link_soups]
        result_dict['language'] = [dict(l.a.attrs)['title'].split(': ')[0] for l in interlanguage_link_soups]
        result_dict['lang'] = [l.text for l in interlanguage_link_soups]
        result_dict['url'] = ['https:' +dict(l.a.attrs)['href'] for l in interlanguage_link_soups]
        df = pd.DataFrame(result_dict)
        return df[df['lang'].str.contains(u'English|Français|Deutsch|EspañolItaliano|Esperanto|Русский|العربية|Latina|Ελληνικά|中文|فارسی|संस्कृतम्')]


# ## Wikitionaries

# In[15]:

def wikitionary(keyword):
    #title = 'dog'
    url = 'http://en.wiktionary.org/w/api.php?format=xml&action=query&prop=revisions&titles={}&rvprop=content'.format(title)
    r = requests.get(url)
    print r.text


# ## 図書館関係

# In[16]:

import requests
from bs4 import BeautifulSoup
import re

class library_info_list(Searcher):
    default_max_page = 20
    
    def __init__(self, keyword, max_page = default_max_page):
        self.keyword = keyword
        self.max_onepage = max_page
        
    def get_hit_num(self, firstpage = 0):
        url = self.get_query(firstpage, max_page = 1)
        r = requests.get(url)
        soup = BeautifulSoup(r.text.encode(r.encoding), "lxml")
        hit_num_result = self.parse_hit_num(soup)
        if hit_num_result:
            return int(hit_num_result.group(1))
        else:
            return 0
        
    def make_resource_list(self):
        last_page = self.get_hit_num()
        return [self.get_query(page, max_page = self.max_onepage) for page in range (0, last_page, self.max_onepage)]
                
    def fetch_data(self, url):
        result_df = pd.DataFrame()
        r = requests.get(url)
        soup = BeautifulSoup(r.text.encode(r.encoding), "lxml")
        for item_soup in self.get_item_soup(soup):
            result_dict = self.parse_data(item_soup)
            result_df = result_df.append(pd.DataFrame(result_dict))
        return result_df
        
    def arrange(self, df):
        if not df.empty:
            df.index = range(1, len(df)+1) #最後にインデックスつけ
        return df


# ## 国会図書館サーチ

# In[17]:

class ndl_list_info(Searcher):
        
    def get_query(self):
        print 'http://iss.ndl.go.jp/api/opensearch?any={}'.format(self.keyword.encode('utf-8'))
        return 'http://iss.ndl.go.jp/api/opensearch?any={}&cnt=500'.format(self.keyword.encode('utf-8'))

    
    def fetch_data(self, soup):
        #基本項目
        basic_tag_list =['category','guid','dc:title','dcndl:titletranscription',
                         'dc:creator','dcndl:edition','dc:publisher','dcterms:issued','dc:subject']
        #print soup
        result_dict = OrderedDict()
        for tag in basic_tag_list:
            tag_soup = soup.find(tag)
            if tag_soup:
                result_dict[tag] = tag_soup.text.strip(),
            else:
                result_dict[tag] = '',

        #identifier
        identifier_type_list = ['dcndl:ISBN', 'dcndl:JPNO']
        for tag in identifier_type_list:
            tag_content = soup.find('dc:identifier', {'xsi:type' : tag})
            if tag_content:
                result_dict[tag] = tag_content.text.strip(),
            else:
                result_dict[tag] = '',
                
        #seeAlso
        result_dict['ndldc_url'] = result_dict['ndlopac_url'] = result_dict['jairo_url'] = result_dict['cinii_url'] = '',
        for also_soup in soup.findAll('rdfs:seealso'):
            resource_url = dict(also_soup.attrs)['rdf:resource']
            if r'http://dl.ndl.go.jp' in resource_url:
                result_dict['ndldc_url']  = resource_url, #デジタルコレクション
            elif r'http://id.ndl.go.jp/bib' in resource_url:
                result_dict['ndlopac_url']  = resource_url, #NDL−OPAC詳細、複写依頼も
            elif r'http://jairo.nii.ac.jp' in resource_url:
                result_dict['jairo_url']  = resource_url, #JAIRO
            elif r'http://ci.nii.ac.jp' in resource_url:
                result_dict['cinii_url']  = resource_url, #CiNii

        return pd.DataFrame(result_dict)
        
    
    def make_resource_list(self):
        url = self.get_query()
        r = requests.get(url)
        soup = BeautifulSoup(r.content, "lxml")
        return soup.findAll("item")
    
    def arrange(self, df):
        if not df.empty:
            df.columns = ['category','ndl_url','title','titletranscription','creator',
                          'edition','publisher','issued','subject','isbn','jpno',
                         'ndldc_url','ndlopac_url','jairo_url','cinii_url']
            df = df.sort_values(by='category')
            df.index = range(1, len(df)+1) #最後にインデックスつけ
        return df
    


# ## CiNii Article

# In[18]:

class CiNii_list_info(library_info_list):
    
    default_max_page = 200
        
    #http://ci.nii.ac.jp/search?q=%E6%96%87%E5%8C%96%E7%A5%AD&range=0&sortorder=1&count=200&start=201
    def get_query(self, page, max_page):
        return 'http://ci.nii.ac.jp/search?' +             'q=' + self.keyword +             '&&range=0&sortorder=1&count=' + str(max_page) + '&start=' + str(page)
    
    def make_resource_list(self):
        last_page = self.get_hit_num()
        return [self.get_query(page, max_page = self.max_onepage) for page in range (1, last_page, self.max_onepage)]

    
    #特異
    def parse_hit_num(self, soup):
#<h1 class="heading"?
# 	<span class="hitNumLabel">検索結果</span>
#
# 	407件中&nbsp;1-200&nbsp;を表示

        hit_soup = soup.find("h1", class_="heading")
        recom = re.compile(u'([0-9]+)件中')
        return recom.search(hit_soup.text)

    def get_item_soup(self, soup):
        return soup.findAll("dl", class_="paper_class")
    
    def get_detail_title(self, soup):
        return soup.find("dt", class_="item_mainTitle item_title").text.strip()

    #     <p class="item_subData item_authordata">
    def get_detail_author(self, soup):
        return soup.find("p", class_="item_subData item_authordata").text.replace('\n','').replace('\t','').strip()
    
    def get_detail_journaldata(self, soup):
        return soup.find("span", class_="journal_title").text.strip()
    
    def get_detail_url(self, soup):
        title_soup = soup.find("dt", class_="item_mainTitle item_title")
        return 'http://ci.nii.ac.jp' + dict(title_soup.a.attrs)['href']
    
    #     <p class="item_otherdata">
    def get_otherdata_url(self, soup):
        title_soup = soup.find("p", class_="item_otherdata")
        if title_soup.a:
            return 'http://ci.nii.ac.jp' + dict(title_soup.a.attrs)['href']
        else:
            return ''
            
    def parse_data(self, soup):
        result_dict = OrderedDict()
        result_dict['title'] = self.get_detail_title(soup),
        result_dict['author'] = self.get_detail_author(soup),
        result_dict['journal'] = self.get_detail_journaldata(soup),
        result_dict['url'] = self.get_detail_url(soup),
        result_dict['ext_url'] = self.get_otherdata_url(soup),
        return result_dict
            


# ## Webcat Plus Minus

# In[19]:

class webcat_list_info(library_info_list):
    
    default_max_page = 300
        
    def get_query(self, page, max_page):
        return 'http://webcatplus.nii.ac.jp/pro/?' +             'q=' + self.keyword +             '&n=' + str(max_page) + '&o=yd&lang=ja&s=' + str(page)
            
    def parse_hit_num(self, soup):
         # <div id="hit">検索結果 803件中
        hit_soup = soup.find("div", id="hit")
        recom = re.compile(r'検索結果 ([0-9]+)件中')
        return recom.search(hit_soup.string.encode('utf-8'))
        
    def fetch_data(self, url):
        result_df = pd.DataFrame()
        r = requests.get(url)
        tree = lxml.html.fromstring(r.content)
        titles = tree.xpath('//*[@id="docs"]/ol/li/div/a')
        descris = tree.xpath('//*[@id="docs"]/ol/li/div[2]')
        for title,descri in zip(titles, descris):
            #print link.text,link.attrib['href'],descri.text
            
            result_dict = OrderedDict()
            result_dict['title'] = title.text,
            result_dict['description'] = descri.text,
            result_dict['url'] = 'http://webcatplus.nii.ac.jp/' + title.attrib['href'],
            result_df = result_df.append(pd.DataFrame(result_dict))
        return result_df
            


# In[20]:

class webcat_list_info_old(library_info_list):
    
    default_max_page = 300
        
    #特異
    def get_query(self, page, max_page):
        return 'http://webcatplus.nii.ac.jp/pro/?' +             'q=' + self.keyword +             '&n=' + str(max_page) + '&o=yd&lang=ja&s=' + str(page)
            
    #特異
    def parse_hit_num(self, soup):
         # <div id="hit">検索結果 803件中
        hit_soup = soup.find("div", id="hit")
        recom = re.compile(r'検索結果 ([0-9]+)件中')
        return recom.search(hit_soup.string.encode('utf-8'))
        
    #<li class="doc">
    #<div class="t"><a href="/webcatplus/details/book/30016474.html" target="webcatplus">深層学習</a></div>
    #<div class="d">岡谷貴之 著, 講談社, 2015.4, 165p, <span class="st">機械学習プロフェッショナルシリーズ / 杉山将 編</span>  </div>
    #</li>

    #特異
    def get_item_soup(self, soup):
        return soup.findAll("li", class_="doc")
    
    #特異
    def get_detail_title(self, soup):
        return soup.find("div", class_="t").text
    
    #特異
    def get_detail_biblio(self, soup):
        return soup.find("div", class_="d").text
    
    #特異
    def get_detail_url(self, soup):
        title_soup = soup.find("div", class_="t")
        return 'http://webcatplus.nii.ac.jp' + dict(title_soup.a.attrs)['href']

    #特異
    def parse_data(self, soup):
        result_dict = OrderedDict()
        result_dict['title'] = self.get_detail_title(soup),
        result_dict['description'] = self.get_detail_biblio(soup),
        result_dict['url'] = self.get_detail_url(soup),
        return result_dict
            


# In[21]:

class  webcat_list_info_title(webcat_list_info):

    def get_query(self, page, max_page):
        return 'http://webcatplus.nii.ac.jp/pro/?' +             't=' + self.keyword +             '&n=' + str(max_page) + '&o=yd&lang=ja&s=' + str(page)

            
class title2webcat_list(Searcher):
    
    def __init__(self, list):
        self.list = list
    
    def make_resource_list(self):
        return self.list
    
    def fetch_data(self, title):
        w = webcat_list_info_title(title)
        return w.collector()

    def arrange(self, df):
        if not df.empty:
            df.index = range(1, len(df)+1) #最後にインデックスつけ
        return df


# In[22]:

class webcat_info(Searcher):
    
    def __init__(self, keyword):
        self.keyword = keyword
            
    def make_resource_list(self):
        wl = webcat_list_info(self.keyword)
        return list(wl.collector()['url'])
    
    def howmany(self):
        return len(self.make_resource_list())
    
    
    def fetch_data(self, url):

        result_df = pd.DataFrame(columns=['isbn','ncid','nbn','title','author','publisher','issued',
                                                                          'pages','summary','contents'])
                                    
        r = requests.get(url)
        soup = BeautifulSoup(r.text.encode(r.encoding), "lxml")

        # ISBN 
        isbn_soup = soup.find('th', text="ISBN")
        if isbn_soup:
            result_df['isbn'] = isbn_soup.next_sibling.next_sibling.text.strip(),
        else:
            result_df['isbn'] = '',

        # NII書誌ID(NCID)
        ncid_soup = soup.find('span', class_="ncid")
        if ncid_soup:
            result_df['ncid'] = ncid_soup.string,
        else:
            result_df['ncid']  = '',

        # 全国書誌番号（JP番号）
        nbn_soup = soup.find('span', class_="nbn")
        if nbn_soup:
            result_df['nbn']  = nbn_soup.string,
        else:
            result_df['nbn']  = '',

        title = ''
        title_soup = soup.find("h2", id="jsid-detailTabTitle")
        if title_soup:
            title  = re.sub(r'[\s]+', " ", title_soup.text)
        else:
            title = ''

        seriestitle_soup = soup.find('th', text="シリーズ名")
        if seriestitle_soup:
            seriestitle = re.sub(r'[\s]+', " ", seriestitle_soup.next_sibling.next_sibling.text)
            title += ' ' + seriestitle
        result_df['title'] = title,

        author_soup = soup.find("p", class_="p-C")
        if author_soup:
            result_df['author'] = author_soup.string,
        else:
            result_df['author'] = '',

        publisher_soup = soup.find('th', text="出版元")
        if publisher_soup:
            result_df['publisher'] = publisher_soup.next_sibling.next_element.next_element.strip(),
        else:
            result_df['publisher'] = '',

        year_soup = soup.find('th', text="刊行年月")
        if year_soup:
            result_df['issued'] = year_soup.next_sibling.next_sibling.string,
        else:
            result_df['issued'] = '',

        page_soup = soup.find('th', text="ページ数")
        if page_soup:
            result_df['pages'] = page_soup.next_sibling.next_sibling.text.strip(),
        else:
            result_df['pages'] = '',

        #概要
        summary_soup = soup.find("div", id="jsid-detailMainText").find("p", class_="p-A")
        if summary_soup:
            result_df['summary'] = summary_soup.string,
        else:
            result_df['summary'] = '',

        #目次
        contents = ''
        mokuji_ul = soup.find("ul", class_="ul-A")
        if mokuji_ul:
            mokuji_list_soup = mokuji_ul.findAll("li")
            for mokuji_item_soup in mokuji_list_soup:
                contents += mokuji_item_soup.string + '\t'

        #掲載作品
        mokuji_div = soup.find("div", class_="table-A")
        if mokuji_div:
            mokuji_list_soup = mokuji_div.findAll("tr")
            for mokuji_item_soup in mokuji_list_soup:
                title_and_author = mokuji_item_soup.text
                title_and_author = re.sub(r'\n[\n\s]+',' - ', title_and_author)
                # print title_and_author.encode('utf-8')
                title_and_author = title_and_author.replace('\n','')
                contents += title_and_author + '\t'
            contents = contents.replace(u'著作名著作者名\t','')
        result_df['contents'] = contents,


#削ったら　2/5の時間で済んだ
# 1 loops, best of 3: 24.8 s per loop
# 1 loops, best of 3: 10.2 s per loop
    
        #NDC,NDCL,値段をNDLへ見に行く
#         result_df['ndc'] = ''
#         result_df['ndlc'] = ''
#         result_df['price'] = ''
#         result_df['ndl_url'] = ''
#         # "http://iss.ndl.go.jp/books/R100000002-I025967743-00.json"
#         ndl_re = re.compile(r'(http://iss.ndl.go.jp/books/[0-9RI\-]+)')
#         ndl_result = ndl_re.search(r.text)
#         if ndl_result:
#             try:
#                 ndl_url = ndl_result.group(0)
#                 ndl_json_url = ndl_url + '.json'
#                 ndl_r = requests.get(ndl_json_url)
#                 ndl_json = ndl_r.json()
#                 # print ndl_json
#                 #分類
#                 if u'subject' in ndl_json:
#                     subject = ndl_json[u'subject']
#                     if u'NDC8' in subject:
#                         result_df['ndc'] = subject[u'NDC8'][0],
#                     elif u'NDC9' in subject:
#                         result_df['ndc']  = subject[u'NDC9'][0],

#                     if u'NDLC' in subject:
#                         result_df['ndlc'] = subject[u'NDLC'][0],
                    
#                     #価格
#                     if u'price' in ndl_json:
#                         result_df['price'] = ndl_json[u'price'],
#                 result_df['ndl_url'] = ndl_url
#             except:
#                 print "can't get: " + ndl_url
 
        return result_df
        
    def arrange(self, df):
        if not df.empty:
            df.index = range(1, len(df)+1) #最後にインデックスつけ
        return df


# ## WorldCat

# In[23]:

class Worldcat_list_info(library_info_list):
    
    default_max_page = 10
        
    #特異
    def get_query(self, page, max_page):
        return 'http://webcatplus.nii.ac.jp/pro/?' +             'q=' + self.keyword +             '&n=' + str(max_page) + '&o=yd&lang=ja&s=' + str(page)
            
    #特異
    def parse_hit_num(self, soup):
         # <div id="hit">検索結果 803件中
        hit_soup = soup.find("div", id="hit")
        recom = re.compile(r'検索結果 ([0-9]+)件中')
        return recom.search(hit_soup.string.encode('utf-8'))
        
    def fetch_data(self, url):
        result_df = pd.DataFrame()
        r = requests.get(url)
        tree = lxml.html.fromstring(r.content)
        titles = tree.xpath('//*[@id="docs"]/ol/li/div/a')
        descris = tree.xpath('//*[@id="docs"]/ol/li/div[2]')
        for title,descri in zip(titles, descris):
            #print link.text,link.attrib['href'],descri.text
            
            result_dict = OrderedDict()
            result_dict['title'] = title.text,
            result_dict['description'] = descri.text,
            result_dict['url'] = 'http://webcatplus.nii.ac.jp/' + title.attrib['href'],
            result_df = result_df.append(pd.DataFrame(result_dict))
        return result_df
        


# ## レファレンス共同データベース

# In[24]:

import urllib2
class refcases_list_info(library_info_list):
    
    default_max_page = 200

    def make_resource_list(self):
        last_page = self.get_hit_num() / self.max_onepage + 1
        return [self.get_query(page, max_page = self.max_onepage) for page in range (1, last_page + 1)]

    def get_query(self, page, max_page):
        query = 'http://crd.ndl.go.jp/reference/modules/d3ndlcrdsearch/index.php?page=detail_list&type=reference'
        query += '&mcmd=' + str(max_page) + '&st=score&asc=desc&kg1=99'
        query +=  '&kw1=' + urllib2.quote(self.keyword.encode('utf-8')) + '&kw_lk1=1&kg2=2&kw2=&kw_lk2=1&kg3=6&pg=' + str(page)
        return query

    def parse_hit_num(self, soup):
        hit_soup = soup.find("div", id="TabbedPanels1")
        recom = re.compile(u'検索結果　([0-9]+)件中')
        return recom.search(soup.text)

    def get_hit_num(self):
        url = self.get_query(page = 1, max_page = 10)
        r = requests.get(url)
        soup = BeautifulSoup(r.text.encode(r.encoding), "lxml")
        hit_num_result = self.parse_hit_num(soup)
        if hit_num_result:
            return int(hit_num_result.group(1))
        else:
            return 0

    def get_item_soup(self, soup):
        table_soup = soup.find('table', class_='slTable')
        return table_soup.findAll('a', {'href':re.compile(r'http://crd.ndl.go.jp/reference/modules/d3ndlcrdentry/index.php?.+')})
    
    def get_detail_title(self, soup):
        return soup.text
    
    def get_detail_url(self, soup):
        return dict(soup.attrs)['href']

    def parse_data(self, soup):
        result_dict = OrderedDict()
        result_dict['title'] = self.get_detail_title(soup),
        result_dict['detail_url'] = self.get_detail_url(soup),
        return result_dict
            


# In[25]:

class Refcases_info(Searcher):
    
    def __init__(self, keyword, search_num):
        self.keyword = keyword
        self.search_num = search_num
            
    def make_resource_list(self):
        rl = refcases_list_info(self.keyword)
        return list(rl.collector()['detail_url'])[:self.search_num]
    
    def howmany(self):
        return len(self.make_resource_list())

    def fetch_data(self, url):

        result_dict = OrderedDict()

        r = requests.get(url)
        soup = BeautifulSoup(r.text.encode(r.encoding), "lxml")

        #<div class="refCaseBox">
        refcases_soup = soup.find('table', class_="refCaseTable")
        th_soups = refcases_soup.findAll('th')
        td_soups = refcases_soup.findAll('td')

        for th_soup, td_soup in zip(th_soups, td_soups):
            result_dict[th_soup.text] = th_soup.next_sibling.text,
        result_dict['url'] = url
        return pd.DataFrame(result_dict)

    def arrange(self, df):
        if not df.empty:
            df.index = range(1, len(df)+1) #最後にインデックスつけ
        return df



# ## 複数のブックリストを束ねて詳細を得る

# In[26]:

class list2webcat_info(webcat_info):
    
    def __init__(self, url_list):
        self.url_list = url_list
            
    def make_resource_list(self):
        return self.url_list


def nbn2webcaturl(nbn):
    return 'http://webcatplus.nii.ac.jp/webcatplus/details/book/nbn/{}.html'.format(nbn)

def ncid2webcaturl(ncid):
    return 'http://webcatplus.nii.ac.jp/webcatplus/details/book/ncid/{}.html'.format(ncid)

def isbn2webcaturl(isbn):
    url = 'http://webcatplus.nii.ac.jp/pro/?i=' + isbn
    content = requests.get(url).text
    soup = BeautifulSoup(content, "lxml")
    title_soup = soup.find('li', class_='doc')
    if title_soup:
        return 'http://webcatplus.nii.ac.jp' + dict(title_soup.find('div', class_='t').a.attrs)['href']
    else:
        return None


def title2webcaturl(title):
    url = 'http://webcatplus.nii.ac.jp/pro/?t=' + title
    content = requests.get(url).text
    soup = BeautifulSoup(content, "lxml")
    title_soup = soup.find('li', class_='doc')
    if title_soup:
        return 'http://webcatplus.nii.ac.jp' + dict(title_soup.find('div', class_='t').a.attrs)['href']
    else:
        return None
    
def asin2webcaturl(asin):
    if asin[0].isdigit():
         #そのままISBNとしてurlをつくる
        return isbn2webcaturl(asin)
    else:
        #Amazonでタイトル取得
        items = item_search(asin)
        title = items[0].find('title').text
        return title2webcaturl (title)

def df2webcaturl(df):
    if 'url' in df.columns and 'http://webcatplus.nii.ac.jp' in df['url'].iat[0]:
        return [url for url in df['url']]
    elif 'isbn' in df.columns:
        return [isbn2webcaturl(isbn) for isbn in df['isbn']]
    elif 'asin' in df.columns:
        return [asin2webcaturl(asin) for asin in df['asin']]
    elif 'title' in df.columns:
        return [title2webcaturl(title) for title in df['title']]

    
def df_list2webcaturl(df_list):
    '''
    ブックリスト系のデータフレームを複数受けて、重複を除いてwebcat詳細ページのurlリストを返す
    '''
    urls =[]
    for df in df_list:
        #print type(df)
        for url in df2webcaturl(df):
            if url and not url in urls:
                urls.append(url)
    return urls


def make_biblio(df_list):
    urls = df_list2webcaturl(df_list)
    #print urls
    w = list2webcat_info(urls)
    return w.collector()




# In[27]:

def keyword2webcaturl(keyword):
    
    url = 'http://webcatplus.nii.ac.jp/pro/?m=b&q=' + keyword
    content = requests.get(url).text
    soup = BeautifulSoup(content, "lxml")
    title_soup = soup.find('li', class_='doc')
    if title_soup:
        #タイトルとurlのリストを返す
        return [title_soup.find('div', class_='t').text, 'http://webcatplus.nii.ac.jp' + dict(title_soup.find('div', class_='t').a.attrs)['href'] ]
    else:
        return None



def textlist2webcaturl(text):
    '''
    text2bib関数の補助というか中身
    '''
    df = pd.DataFrame(columns=['description','url'])
    for line in text.split('\n'):
        #print 'this book is being searched ' + line
        line = re.sub(u'[『』、,]', ' ', line)
        splited_line = line.split()
        #見つかるまで少しずつキーワードを縮めていく（最低２個）
        for i in range(len(splited_line),1,-1):
            keyword = '+'.join(splited_line[0:i])
            #print keyword
            now_result = keyword2webcaturl(keyword)
            if now_result:
                #print 'hit ' +now_result[0] + now_result[1]
                df = df.append(pd.DataFrame({'description':[line],'url':[now_result[1]]}))
                break
    df.index = range(1, len(df)+1) #最後にインデックスつけ
    return df

@register_cell_magic
def text2bib(line, cell):
    '''
    テキスト形式の書誌情報からwebcat pro詳細ページのurlを取得して書誌データフレームに統合できる形式で返す
    
    返り値：DataFrame
    
    書式：
    %%text2bib
    （書誌情報1：タイトル 著者名 など；スペースなどで区切る。次項目とは改行区切り）
    （書誌情報2：タイトル 著者名 など；スペースなどで区切る。次項目とは改行区切り）
　　……
    
    例：
    %%text2bib
    フランクリン R.バーリンゲーム 中村保男訳. 時事通信社, 1956. 
    フランクリン研究 その経済思想を中心として 久保芳和 関書院, 1957. 
    フランクリンとアメリカ文学 渡辺利雄 研究社出版, 1980.4. 研究社選書 
    進歩がまだ希望であった頃 フランクリンと福沢諭吉 平川祐弘 新潮社, 1984.9. のち講談社学術文庫 
    フランクリン 板倉聖宣 仮説社, 1996.8. やまねこ文庫 
    ベンジャミン・フランクリン、アメリカ人になる ゴードン・S・ウッド 池田年穂,金井光太朗,肥後本芳男訳. 慶應義塾大学出版会
    '''
    sio = StringIO(cell)
    return textlist2webcaturl(sio.getvalue())


# ## Amazon Review

# In[28]:

def isbn13to10(isbn):
    #978-4-532-35628-6
    isbn = isbn.replace('-','')
    a = re.search(r'978([0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9])[0-9]', str(isbn))
    if a:
        isbn9 = a.group(1).replace('-','')
        #print isbn9
        list_ismb9 = list(str(isbn9))
        #print list_ismb9
        list_ismb9.reverse()
        sum = 0
        w = 2
        for i in list_ismb9:
            sum += int(i) * w
            w += 1
        d = 11 - (sum % 11)
        if d == 11:
            d = '0'
        elif d == 10:
            d = 'x'
        else:
            d = str(d)
        return isbn9 + d
    else:
        return isbn

def get_review_url(ASIN):
    return 'http://www.amazon.co.jp/product-reviews/' +         str(ASIN) + '/ref=cm_cr_dp_see_all_summary?ie=UTF8&showViewpoints=1&sortBy=byRankDescending'
    
# def get_review_url2(ASIN):
#     return 'http://www.amazon.co.jp/product-reviews/' + \
#         str(ASIN) + '/ref=cm_cr_dp_see_all_summary?ie=UTF8&pageNumber=2&sortBy=byRankDescending'

#     <span class="a-size-medium a-text-beside-button totalReviewCount">18</span>

def fetch_review(url):
    r = requests.get(url)
    if r.status_code == 200:
        # soup = BeautifulSoup(r.text.encode(r.encoding), "html.parser")
        soup = BeautifulSoup(r.text.encode('utf-8'), "lxml")
        #<span class="a-size-base review-text">レビュー</span>
        review_title_list = soup.findAll("a", class_="a-size-base a-link-normal review-title a-color-base a-text-bold")
        review_list = soup.findAll("span", class_="a-size-base review-text")
        review_buffer =''
        for review_title, review_item in zip(review_title_list, review_list):
            review_buffer += u'◯' +review_title.text +u'：'+ review_item.text+'\t'
        return review_buffer

def amazon_review(ISBN):
    return fetch_review(get_review_url(isbn13to10(ISBN)))


    
class amazon_reviews(Searcher):
    
    def __init__(self, df):
        self.biblio_df = df
        
    def make_resource_list(self):
        if 'isbn' in self.biblio_df.columns:
            return list(self.biblio_df['isbn'])
        elif 'asin' in self.biblio_df.columns:
            return list(self.biblio_df['asin'])
        else:
            return None
    
    
    def fetch_data(self, isbn):
        result_df = pd.DataFrame()
        if isbn:
            url = get_review_url(isbn13to10(isbn))
            r = requests.get(url)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text.encode('utf-8'), "lxml")
                review_book = soup.find('a',class_="a-size-large a-link-normal")
                review_title_list = soup.findAll("a", class_="a-size-base a-link-normal review-title a-color-base a-text-bold")
                review_list = soup.findAll("span", class_="a-size-base review-text")

                for review_title, review_item in zip(review_title_list, review_list):
                    result_dict = OrderedDict()
                    result_dict['isbn'] = isbn,
                    result_dict['book_title'] = review_book.text,
                    result_dict['review_title'] = review_title.text,
                    result_dict['description'] = review_item.text,
                    result_dict['des_size'] = len(review_item.text),
                    result_df = result_df.append(pd.DataFrame(result_dict))
        return result_df
    

 
    def arrange(self, df):
        if not df.empty:
            df.sort_values(by='book_title')
            df.index = range(1, len(df)+1) #最後にインデックスつけ
        return df




# ## 所在情報 

# ## カリール 

# In[29]:

liblary_columns=['systemid','systemname','formal','address','tel','geocode','category','url_pc']

def near_libraries_df(locate):
    '''
    地名を渡して付近の図書館のリスト（館名、住所、電話、geocode、URLなど）のデータフレームを返す
    '''
    df = pd.DataFrame(columns=liblary_columns)
    #print locate
    geocoding_url = 'http://www.geocoding.jp/api/?v=1.1&q={}'.format(locate.encode('utf-8'))
    r = requests.get(geocoding_url)
    soup = BeautifulSoup(r.text.encode(r.encoding),"lxml")
    #print soup
    lng = soup.find('lng').text
    lat = soup.find('lat').text
    url = 'http://api.calil.jp/library?appkey={}&geocode={},{}'.format(calil_app_key, lng, lat)
    r = requests.get(url)
    soup = BeautifulSoup(r.text.encode(r.encoding),"lxml")
    libraries = soup.findAll('library')
    for library_soup in libraries:
        now_dict = OrderedDict()
        for now_column in liblary_columns:
            now_dict[now_column] = [library_soup.find(now_column).text]
        df = df.append(pd.DataFrame(now_dict))
    df.index = range(1, len(df)+1) #最後にインデックスつけ
    return df

def prefecture_libraries_df(locate):
    df = pd.DataFrame(columns=liblary_columns)
    url = 'http://api.calil.jp/library?appkey={}&pref={}'.format(calil_app_key, locate.encode('utf-8'))
    r = requests.get(url)
    soup = BeautifulSoup(r.content,"lxml")
    libraries = soup.findAll('library')
    for library_soup in libraries:
        now_dict = OrderedDict()
        for now_column in liblary_columns:
            now_dict[now_column] = [library_soup.find(now_column).text]
        df = df.append(pd.DataFrame(now_dict))
    df.index = range(1, len(df)+1) #最後にインデックスつけ
    return df

def one_city_libraries_df(pref, city):
    df = pd.DataFrame(columns=liblary_columns)
    url = 'http://api.calil.jp/library?appkey={}&pref={}&city={}'.format(calil_app_key, pref.encode('utf-8'), city.encode('utf-8'))
    #print url
    r = requests.get(url)
    soup = BeautifulSoup(r.content,"lxml")
    #print soup
    libraries = soup.findAll('library')
    for library_soup in libraries:
        now_dict = OrderedDict()
        for now_column in liblary_columns:
            now_dict[now_column] = [library_soup.find(now_column).text]
        df = df.append(pd.DataFrame(now_dict))
    df.index = range(1, len(df)+1) #最後にインデックスつけ
    return df


def city_libraries_df(locate):
    url = 'http://geoapi.heartrails.com/api/xml?method=suggest&matching=like&keyword={}'.format(locate.encode('utf-8'))
    r = requests.get(url)
    soup = BeautifulSoup(r.content,"lxml")
    #print soup, soup.find('error')
    if soup.find('error'):
        #市町村名じゃなかったら、近隣を探す
        print locate,'付近の図書館を検索'
        return near_libraries_df(locate)
    else:
        #市町村名なら県名と市町村名を得て、それで探す
        pref = soup.find('prefecture').text
        city = soup.find('city').text
        #print pref, city
        if u'区' in city:
            #政令指定都市は区が入ってるので取り除く
            city = re.sub(u'[^市]+区', '', city)
        #print pref, city
        print pref, city, '内の図書館を検索'
        return one_city_libraries_df(pref, city)
    

prefectures = [u'北海道',u'青森県',u'岩手県',u'宮城県',u'秋田県',u'山形県',u'福島県',u'茨城県',u'栃木県',u'群馬県',
               u'埼玉県',u'千葉県',u'東京都',u'神奈川県',u'新潟県',u'富山県',u'石川県',u'福井県',u'山梨県',u'長野県',
               u'岐阜県',u'静岡県',u'愛知県',u'三重県',u'滋賀県',u'京都府',u'大阪府',u'兵庫県',u'奈良県',u'和歌山県',
               u'鳥取県',u'島根県',u'岡山県',u'広島県',u'山口県',u'徳島県',u'香川県',u'愛媛県',u'高知県',u'福岡県',
               u'佐賀県',u'長崎県',u'熊本県',u'大分県',u'宮崎県',u'鹿児島県',u'沖縄県']

def library_list(locate_list):
    '''
    地名のリストを渡して付近の図書館のリスト（館名、住所、電話、geocode、URLなど）のデータフレームを返す
    '''
    df = pd.DataFrame()
    for locate in locate_list:
        if locate in prefectures:
            #県名のみなら県内の一覧を返す
            df = df.append(prefecture_libraries_df(locate))
        else:
            df = df.append(city_libraries_df(locate))
    df.index = range(1, len(df)+1) #最後にインデックスつけ
    return df




# In[30]:

import time

def get_library_data(df, now_systemid, request_column):
    return df[df['systemid']==now_systemid][request_column].values[0]

def get_biblio_data(df, now_isbn, request_column):
    return df[df['isbn']==now_isbn][request_column].values[0]


def library_status(biblio_df, library_df = MYLIBRARY):
    '''
    isbnを含むbiblioデータフレームと図書館リストのデータフレームを渡して、
    isbn、タイトル、所蔵／貸し出し状況／予約URLについてデータフレームにまとめて返す
    '''
    isbn_list  = [isbn for isbn in biblio_df['isbn']]
    library_list = [library for library in library_df['systemid']]
    
    df = pd.DataFrame(columns=['isbn','title','library','status','url'])

    #一回目のリクエスト
    api = 'http://api.calil.jp/check?appkey={}&isbn={}&systemid={}&format=xml'.format(calil_app_key, ','.join(isbn_list), ','.join(library_list))
    r = requests.get(api)
    soup = BeautifulSoup(r.text.encode('utf-8'),"lxml")

    #終了かどうか状況取得  0（偽）または1（真）。1の場合は、まだすべての取得が完了していない.
    now_continue = soup.find('continue').text

    while '0' not in now_continue:
        #セッション情報取得
        now_session = soup.find('session').text
        #５秒待つ
        time.sleep(5)
        #再度のリクエスト
        #print now_continue, "I'm waiting..."
        api  = 'http://api.calil.jp/check?appkey={}&session={}&format=xml'.format(calil_app_key, now_session)
        r = requests.get(api)
        soup = BeautifulSoup(r.text.encode('utf-8'),"lxml")
        now_continue = soup.find('continue').text

    #ループを抜けたらパース処理
    books = soup.findAll('book')
    for booksoup in books:
        now_isbn = dict(booksoup.attrs)['isbn']
        #本ごとの下に各館の状況
        librarysoups = booksoup.findAll('system')
        for librarysoup in librarysoups:
            #各館の下に貸出状況
            now_systemid = dict(librarysoup.attrs)['systemid']
            now_libkeys_soup = librarysoup.find('libkeys')
            if now_libkeys_soup and now_libkeys_soup.text:
                #libkeysがあれば本がある
                now_libkeys = now_libkeys_soup.text
                now_reserveurl = librarysoup.find('reserveurl').text
            else:
                now_libkeys = 'None'
                now_reserveurl = 'None'
            now_dict = OrderedDict()
            now_dict['isbn']  = now_isbn,
            now_dict['title']  = get_biblio_data(biblio_df, now_isbn, 'title'),
            now_dict['library']  = get_library_data(library_df, now_systemid, 'formal'),
            now_dict['status']  =now_libkeys,
            now_dict['url']  =now_reserveurl,
            df = df.append(pd.DataFrame(now_dict))
    df = df[df['status']!='None']
    df.index = range(1, len(df)+1)  #最後にインデックスつけ
    return df




# ## アマゾンの在庫／最安値チェック

# In[31]:

def amazon_stock_thisbook(keyword):
    result_df = pd.DataFrame()
    book_soups = item_search(keyword)
    if book_soups:
        for book_soup in book_soups:
            result_dict = OrderedDict()
            result_dict['asin'] = book_soup.find('asin').text,
            result_dict['title'] = book_soup.find('title').text,
            if book_soup.find('formattedprice'):
                result_dict['listprice'] = book_soup.find('formattedprice').text,
            offersummary_soup = book_soup.find('offersummary')
            if offersummary_soup:
                #print keyword, offersummary_soup
                result_dict['totalnew'] = offersummary_soup.find('totalnew').text,
                if offersummary_soup.find('lowestnewprice'):
                    result_dict['lowestnewprice'] = offersummary_soup.find('lowestnewprice').find('formattedprice').text,
                else:
                    result_dict['lowestnewprice'] = 'None',
                result_dict['totalused'] = offersummary_soup.find('totalused').text,
                if offersummary_soup.find('lowestusedprice'):
                    result_dict['lowestusedprice'] = offersummary_soup.find('lowestusedprice').find('formattedprice').text,
                else:
                    result_dict['lowestusedprice'] = 'None',
            result_dict['url'] = 'http://www.amazon.co.jp/dp/{}/'.format(book_soup.find('asin').text)
            result_df = result_df.append(pd.DataFrame(result_dict))
    return result_df

def ciniibook_title(ncid):
    url = 'http://ci.nii.ac.jp/ncid/{}'.format(ncid)
    r = requests.get(url)
    soup = BeautifulSoup(r.text.encode('utf-8'),"lxml")
    book_title_soup = soup.find('meta', attrs={'name':'dc.title'})
    if book_title_soup:
        return dict(book_title_soup.attrs)['content']
    
def amazon_stocks(biblio_df):
    result_df = pd.DataFrame(columns=['asin','title','listprice','totalnew','lowestnewprice','totalused','lowestusedprice','url'])
    for i in range(0, len(biblio_df)):
        print '.',
        if 'isbn' in biblio_df.columns:
            isbn = isbn13to10(biblio_df['isbn'].iat[i])
        elif 'asin' in biblio_df.columns:
            isbn = biblio_df['asin'].iat[i]
        else:
            isbn = None
        if 'ncid' in biblio_df.columns:
            ncid = biblio_df['ncid'].iat[i]
        else:
            ncid = None
        if 'title' in biblio_df.columns:
            title = biblio_df['title'].iat[i]
        else:
            title  = None

        
        if isbn and len(amazon_stock_thisbook(isbn)):
            result_df = result_df.append(amazon_stock_thisbook(isbn))
        elif ncid and ciniibook_title(ncid):
            result_df = result_df.append(amazon_stock_thisbook(ciniibook_title(ncid)))
        elif len(amazon_stock_thisbook(unicode(title))):
            result_df = result_df.append(amazon_stock_thisbook(unicode(title)))
        else:
            result_dict = OrderedDict()
            result_dict['asin'] = isbn,
            result_dict['title'] = title,
            result_dict['listprice'] = 'None',
            result_dict['totalnew'] = 'None',
            result_dict['lowestnewprice'] = 'None',
            result_dict['totalused'] ='None',
            result_dict['lowestusedprice'] = 'None',
            result_dict['url'] = 'None',
            result_df = result_df.append(pd.DataFrame(result_dict))
    result_df = result_df.sort_values(by='title')
    result_df.index = range(1, len(result_df)+1) #最後にインデックスつけ
    return result_df
 
    


# ## 日本の古本屋

# In[32]:

class Kosho_info(library_info_list):
    
    default_max_page = 100
   
    #https://www.kosho.or.jp/products/list.php?transactionid=f933edac26fe92ced0cdfbbd118b58d90e5e59f9&mode=search_retry&pageno=2&search_pageno=1&product_id=&reset_baseinfo_id=&baseinfo_id=&product_class_id=&quantity=1&from_mode=&search_facet_publisher=&search_word=%E6%A0%AA%E5%BC%8F%E6%8A%95%E8%B3%87&search_name=&search_name_matchtype=like&search_author=&search_author_matchtype=like&search_publisher=&search_publisher_matchtype=like&search_isbn=&search_published_year_min=&search_published_year_max=&search_comment4=&search_comment4_matchtype=like&search_book_flg=&search_price_min=&search_price_max=&search_only_has_stock=1&search_orderby=score&search_sorttype=asc&search_page_max=20&search_image_disp=&search_orderby_navi=score&search_sorttype_navi=asc&search_page_max_navi=20&search_image_disp_navi=&transactionid=f933edac26fe92ced0cdfbbd118b58d90e5e59f9
    def get_query(self, page, max_page):
        return 'https://www.kosho.or.jp/products/list.php?mode=search_retry&pageno=' + str(page) +             '&search_pageno=1&quantity=1&search_word=' + self.keyword +             '&search_only_has_stock=1&search_orderby=score&search_sorttype=asc&search_page_max=' + str(max_page) 
    
    def make_resource_list(self):
        last_page = self.get_hit_num() / self.max_onepage + 1
        return [self.get_query(page, max_page = self.max_onepage) for page in range (1, last_page + 1)]

    
    #<form name="form1"
    # <!--★件数-->
    #<div><span class="attention">134件</span>が見つかりました。</div>
    def parse_hit_num(self, soup):
        hit_soup = soup.find("form", id="form1")
        recom = re.compile(u'([0-9]+)件が見つかりました。')
        return recom.search(hit_soup.text)
    

    #<div class="search_result_list product_list">
    def get_item_soup(self, soup):
        return soup.findAll("div", class_="search_result_list product_list")
    
    #<a href="javascript:goDetail(5185060);">株式投資＝はじめるまえの50の常識</a>
    def get_detail_title(self, soup):
        return soup.find('a', {'href':re.compile(r'javascript:goDetail.+')}).text.strip()

    #https://www.kosho.or.jp/products/detail.php?product_id=5185060
    def get_detail_url(self, soup):
        title_soup = soup.find('a', {'href':re.compile(r'javascript:goDetail.+')})
        recom = re.compile(r'javascript:goDetail\(([0-9]+)\);')
        m = recom.search(dict(title_soup.attrs)['href'])
        return 'https://www.kosho.or.jp/products/detail.php?product_id=' + m.group(1)

    
    #<div class="product_info wide">または<div class="product_info">
    def get_detail_productinfo(self, soup):
        info_soup = soup.find("div", class_=re.compile(r'product_info.*'))
        if info_soup:
            return info_soup.text.replace('\n','').replace('\t','').strip()
        else:
            return ''
    #<span class="price">3,500</span>
    def get_detail_price(self, soup):
        return soup.find('span', class_='price').text.strip()
            

    #特異
    def parse_data(self, soup):
        result_dict = OrderedDict()
        result_dict['title'] = self.get_detail_title(soup),
        result_dict['info'] = self.get_detail_productinfo(soup),
        result_dict['price'] = self.get_detail_price(soup),
        result_dict['url'] = self.get_detail_url(soup),
        return result_dict


class Kosho_info_title(Kosho_info):
       #https://www.kosho.or.jp/products/list.php?
        #mode=search_retry&pageno=&search_pageno=1&product_id=&reset_baseinfo_id=&
        #baseinfo_id=&product_class_id=&quantity=1&from_mode=&search_facet_publisher=
        #&search_word=&search_name=%E7%A9%BA%E3%81%AE%E8%89%B2%E3%81%AB%E3%81%AB%E3%81%A6%E3%81%84%E3%82%8B

        def get_query(self, page, max_page):
            return 'https://www.kosho.or.jp/products/list.php?' +                         'mode=search_retry&pageno=&search_pageno=1&product_id=&reset_baseinfo_id=&' +                         'baseinfo_id=&product_class_id=&quantity=1&from_mode=&search_facet_publisher=' +                         '&search_only_has_stock=1&search_word=&search_name=' +self.keyword
                


def kosho_stocks(biblio_df):
    result_df = pd.DataFrame()
    for i in range(0, len(biblio_df)):
        title = biblio_df['title'].iat[i]
        k = Kosho_info_title(title)
        df = k.collector()
        result_df = result_df.append(df)
    result_df = result_df.sort_values(by='title')
    result_df.index = range(1, len(result_df)+1) #最後にインデックスつけ
    return result_df



# ## 国会図書館・各県立図書館

# In[33]:

def house_books(soup):
    #所蔵館と貸し出し状況
    items = soup.findAll('dcndl:item')
    #result = u'所蔵館数：' + unicode( len(items)) + '\n'
    
    result_df = pd.DataFrame(columns=['title','library_name','availability','description','url'])
    
    for item in items:
        print '.',
        result_dict = OrderedDict()
        result_dict['title'] = soup.find('dcterms:title').text,
        result_dict['library_name'] = item.find('foaf:name').text,
        result_dict['availability']  = result_dict['description'] = result_dict['url'] ='',
        if item.find('dcndl:availability'):
            result_dict['availability'] = item.find('dcndl:availability').text,
        if item.find('dcterms:description'):
            result_dict['description'] = item.find('dcterms:description').text,
        if item.find('rdfs:seealso'):
            result_dict['url'] = dict(item.find('rdfs:seealso').attrs)['rdf:resource']  #各図書館の詳細ページ
        result_df = result_df.append(pd.DataFrame(result_dict))
    
    return result_df


def nbn2ndlurl(nbn):
    url ='http://iss.ndl.go.jp/api/opensearch?jpno={}'.format(nbn)
    #print (url)
    try:
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.content, "lxml")
        guid = soup.find('guid', ispermalink='true')
        return guid.text
    except:
        return None
        

def ndl_stocks(df):
    result_df = pd.DataFrame(columns=['title','library_name','availability','description','url'])
    for nbn in df['nbn']:
        url = nbn2ndlurl(nbn)
        if url:
            url_rdf = url + '.rdf'
            r = requests.get(url_rdf)
            soup = BeautifulSoup(r.content, "lxml")
            result_df = result_df.append(house_books(soup))
    result_df.index = range(1, len(result_df)+1) #最後にインデックスつけ
    return result_df
        



# ## 国会図書館デジタルコレクション、複写サービス、外部リポジトリ

# In[34]:

def ndl_collection(df):
    result_df = pd.DataFrame()

    basic_term_list = ['dcterms:title','dc:creator','dcterms:issued']
    resource_list=[r'id.ndl.go.jp',r'dl.ndl.go.jp',r'ci.nii.ac.jp',r'jairo.nii.ac.jp']

    for url in df['ndl_url']:

        url_rdf = url + '.rdf'
        r = requests.get(url_rdf)
        soup = BeautifulSoup(r.content, "lxml")
        #print soup
        result_dict = OrderedDict()

        for basic_term in basic_term_list:
                if soup.find(basic_term):
                    result_dict[basic_term] = soup.find(basic_term).text,
                else:
                    result_dict[basic_term] = '',

        for resource in resource_list:
            result_dict[resource] = ''
        seealso_soups = soup.findAll('rdfs:seealso')
        for seealso_soup in seealso_soups:
            #print seealso_soup
            seealso_url = dict(seealso_soup.attrs)['rdf:resource']
            #print seealso_url
            for resource in resource_list:
                if resource in seealso_url:
                    #print resource
                    result_dict[resource] = seealso_url,
        result_df = result_df.append(pd.DataFrame(result_dict))
    result_df.index = range(1, len(result_df)+1) #最後にインデックスつけ
    return result_df




# ## Google検索

# In[35]:

class Google_info(Searcher):
        
    default_max_page = 50
        
    # https://www.google.co.jp/search?q=[keyword]&num=10&start=10
    def get_query(self, page, max_page):
        return 'https://www.google.co.jp/search?q={}&num={}&start={}'.format(self.keyword.encode('utf-8'),max_page,page)
    
    def make_resource_list(self):
        last_page = 50
        return [self.get_query(page, self.default_max_page) for page in range (0, last_page, self.default_max_page)]

    def fetch_data(self, url):
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}
        r = requests.get(url,  headers=headers)
        tree = lxml.html.fromstring(r.content.decode('utf-8'))

        h3_soups = tree.xpath('//h3[@class="r"]/a')
        st_soups = tree.xpath('//span[@class="st"]')
        df = pd.DataFrame()
        for i_h3,i_st in zip(h3_soups, st_soups):
            result_dict = OrderedDict()
            result_dict['title'] = i_h3.text,
            result_dict['summary'] = i_st.text_content(),
            result_dict['url'] = i_h3.attrib['href'],
            df = df.append(pd.DataFrame(result_dict))
        return df  
    
    def arrange(self, df):
        if not df.empty:
            df.index = range(1, len(df)+1) #最後にインデックスつけ
        return df



# In[36]:

class Google_book_info(Google_info):
        
    def get_query(self, page, max_page):
        return 'https://www.google.co.jp/search?tbm=bks&q={}&num={}&start={}'        .format(self.keyword.encode('utf-8'),max_page,page)



# ## Graphviz関係

# In[37]:

#インラインでdot言語を表示する

def embed_dot(dot_string, size=''):
    G=pgv.AGraph(dot_string)
    G.graph_attr.update(size='{}'.format(size))
    G.layout()
    output = cStringIO.StringIO()
    G.draw(output, format='svg')
    svg = output.getvalue()
    output.close()
    svg_core = BeautifulSoup(svg, 'lxml').find('svg')
    return HTML(unicode(svg_core))


# In[38]:

@register_cell_magic
def csv2dot(line, cell):
    '''
    コンマ区切りのテキストからネットワーク図をつくる
    
    書式例:
    %%csv2dot
    角倉了以,日本大百科全書,角倉了以とその子
    角倉了以,朝日日本歴史人物事典,「角倉文書」(『大日本史料』12編14所収)
    角倉了以,参考調査便覧,宮本又次他『日本貿易人の系譜』有斐閣1980
    '''
    G = pgv.AGraph(strict=False,directed=True)
    G.graph_attr.update(layout = 'dot', rankdir='LR', concentrate = 'true')
    for line in cell.split('\n'):
        items = line.split(',')
        for i in range(len(items))[:-1]:
            print items[i],'->', items[i+1]
            G.add_edge(items[i], items[i+1])
    return embed_dot(G.to_string())


# In[39]:

@register_cell_magic
def indent2dot(line, cell):
    '''
    タブ区切りのインデント付きテキストからネットワーク図をつくる
    
    書式例:
    %%csv2dot
    角倉了以
        日本大百科全書
            角倉了以とその子
        朝日日本歴史人物事典
            「角倉文書」(『大日本史料』12編14所収)
            角倉了以とその子
        参考調査便覧
            宮本又次他『日本貿易人の系譜』有斐閣1980
    '''
    G = pgv.AGraph(strict=False,directed=True)
    G.graph_attr.update(layout = 'dot', rankdir='LR', concentrate = 'true')
    node_stack = [cell.split('\n')[0]]
    
    for line in cell.split('\n')[1:]:
        #print line, line.count('    ',0), len(node_stack),node_stack
        if len(node_stack) < line.count('    ',0)+1:
            #１つ下がる
            node_stack.append(line.strip())
        elif len(node_stack) == line.count('    ',0)+1:
            #同じレベル
            node_stack.pop()   
            node_stack.append(line.strip())
        elif len(node_stack) > line.count('    ',0)+1:
            node_stack.pop()
            node_stack.pop()
            node_stack.append(line.strip())
        G.add_edge(node_stack[-2], node_stack[-1])
        #print node_stack[-2],'->', node_stack[-1]
    return embed_dot(G.to_string())


# ## Thema Map by Wikipedia Category

# In[40]:

class Thememap(object):

    def __init__(self, first_keyword, max_level = 2):
        self.G = pgv.AGraph(strict=False,directed=True)
        self.first_keyword = first_keyword.decode('utf-8')
        self.max_level = max_level
        self.all_categories = []
        self.node_links = {}

        # キーワードを受けて上位概念のリストを返す
    def fetch_category(self, keyword):
        url = "https://ja.wikipedia.org/wiki/" + keyword
        r = requests.get(url)
        soup = BeautifulSoup(r.text.encode('utf-8'),"lxml")

        return_buffer = []
        # 上位概念はカテゴリから抽出
        #<div id="mw-normal-catlinks" class="mw-normal-catlinks">
        # <li><a href="/wiki/Category:%E9%8A%80%E8%A1%8C" title="Category:銀行">銀行</a></li>
        category_div_soup = soup.find("div", class_="mw-normal-catlinks")
        if category_div_soup:
            category_list_soup = category_div_soup.findAll("li")
            for category_soup in category_list_soup:
                return_buffer.append(category_soup.a.string)
            return return_buffer

#     def fetch_category(self, keyword):
#         import wikipedia
#         wikipedia.set_lang("ja")
#         hit = wikipedia.page(keyword)
#         return [c for c in hit.categories]

    def regist_link(self, link_name, link_words):
        # 短いリンクを優先
        if not self.node_links.has_key(link_name):
            self.node_links[link_name] = link_words

    def dot(self, start_word, now_level):
        if now_level > self.max_level:
            return
        else:
            now_fetch_categories = self.fetch_category(start_word)
            if now_fetch_categories:
                for now_category in now_fetch_categories:
                    print '.',
                    # print now_category
                    if now_category in self.all_categories:
                        continue
                    else:
                        # print now_category のカテゴリ
                        link_word = start_word
                        start_word = start_word.replace(u'Category:','')
                        start_word = start_word.replace(u'のカテゴリ','')
                        self.regist_link(start_word, link_word)
                        if now_level+1 > self.max_level:
                            #枝の先は未処理になるのでここでリンクだけつくっておく
                            self.regist_link(now_category, u'Category:'+now_category)
                        
                        #エッジを追加
                        self.G.add_edge(start_word, now_category)
                        
                        #一度出てきたカテゴリは記録して重複を防ぐ
                        self.all_categories.append(now_category)
                        #下位レベルへ再帰
                        self.dot('Category:'+now_category,  now_level+1)


    def draw(self):
        self.dot(self.first_keyword, 0)
        
        #　ノードごとにurlリンクをつける
        for link_name, link_word in self.node_links.items():
            self.G.add_node(link_name, shape = 'plaintext', href='https://ja.wikipedia.org/wiki/' + link_word)

        self.G.graph_attr.update(layout = 'dot', rankdir='LR', concentrate = 'true')
        return self.G.to_string()



# ## Google Suggest Map

# In[41]:

def uniq(seq):
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if x not in seen and not seen_add(x)]
    
class SuggestMap(object):
    
    def __init__(self, keyword, expand_flag=0):
        self.keyword = keyword
        self.expand_flag = expand_flag
        self.suggested_list = []
        self.node_links = {}
        self.row = "digraph{ graph[layout = neato, concentrate = true, overlap = false, splines = true];"
        self.row += self.keyword +' [shape=circle];\n'
        self.row += 'node [shape = plaintext];\n'

    
    #googleサジェストで情報集め
    def suggest(self, keyword):
        suggested_list = []
        tail_list = ['',' ','_']

        # 時間はかかるけど豊かなマップが書けるオプション
        if self.expand_flag == 1:
            tail_list.extend([' ' + unichr(i+97) for i in range(26)]) #アルファベット全部
            #２回めは添付しないとかなり時間は短縮できて結果は同じ
            self.expand_flag = 0
        elif self.expand_flag == 2:
            tail_list.extend([' ' + unichr(i+12450) for i in range(89)]) #カタカナ全部
            #２回めは添付しないとかなり時間は短縮できて結果は同じ
            self.expand_flag = 0

        for tail in tail_list:
            url = "http://www.google.com/complete/search?hl=ja&q="+keyword+tail+"&output=toolbar"
            #print url.encode('utf-8')
            r = requests.get(url)
            # print r.encoding
            soup = BeautifulSoup(r.text.encode('utf-8'),"lxml")
            #<suggestion data="機械翻訳 比較"/>
            suggest_list_soup = soup.findAll("suggestion")
            for suggest_soup in suggest_list_soup:
                print '.',
                now_suggested_text = dict(suggest_soup.attrs)['data']
                now_suggested = keyword + ' ' + now_suggested_text
                # 重複外し
                now_suggested = ' '.join(uniq(now_suggested.split(' ')))
                suggested_list.append(now_suggested)

        return suggested_list

    def regist_link(self, link_name, suggested_words):
        # 短いリンクを優先
        # print 'リンクする', link_name, suggested_words,len(suggested_words.split('+'))
        if self.node_links.has_key(link_name):
            # print 'リンク既出：', node_links[link_name],len(node_links[link_name].split(' '))
            if len(self.node_links[link_name].split(' ')) > len(suggested_words.split(' ')):
                # print 'よりシンプルなリンクなので：登録'
                self.node_links[link_name] = suggested_words
        else:
            # print 'リンク初出：登録'
            self.node_links[link_name] = suggested_words    

    def get_src_link(self, now_suggested):
        # print now_suggested.encode('utf-8')
        now_src = '"' + re.sub(r'[\s]+', '" -> "', now_suggested) + '";\n'
        # 孔子 [href="http://ja.wikipedia.org/wiki/孔子"];
        if  now_suggested.split(' ')[-1] in self.keyword:
            self.regist_link(now_suggested.split(' ')[0] ,now_suggested)
        # print now_node_link.encode('utf-8')        
        else:
            self.regist_link(now_suggested.split(' ')[-1] ,now_suggested)
        return now_src


    def draw(self):
        first_list = self.suggest(self.keyword)
        suggested_list = first_list
        src = ''
        for key in first_list:
            for now_suggested in self.suggest(key):
                src += self.get_src_link(now_suggested)

        node_link_buffer = ''
        for link_name, suggested_words in self.node_links.items():
            node_link_buffer += '"'+ link_name + '" [href="https://www.google.co.jp/search?q='+suggested_words+'"];\n'

        self.row += node_link_buffer + src + '}'
        
        return self.row



# ### 関連マップの元

# In[42]:

class RelateMap(object):
        
    def __init__(self, keyword, max_depth,  max_width):
        print 'depth: ' + str(max_depth) + '  width: ' + str(max_width)
        self.G = pgv.AGraph(strict=False,directed=True)
        self.keyword = keyword
        self.max_depth = max_depth
        self.max_width = max_width
        self.construct_graph()
        
    def construct_graph(self):
        start_nodes = self.get_start_node()
        for start_node in start_nodes:
            self.build_edges(start_node, 0)
        self.set_nodes_attr()
        self.set_graph_attr()
            

    def build_edges(self, start_node, now_depth):
        if now_depth >= self.max_depth:
            return
        for next_node in self.get_nextnodes(start_node):
            print '.',
            self.G.add_edge(start_node, next_node)
            self.build_edges(next_node, now_depth +1)

    def set_nodes_attr(self):
        for n in self.G.nodes():
            print '.',
            nlabel = self.get_node_label(n)
            nxlabel = self.get_node_xlabel(n)
            nshape = self.get_node_shape(n)
            nhref  = self.get_node_href(n)
            nimage  = self.get_node_image(n)
            self.G.add_node(n, label = nlabel, bottomlabel= nxlabel, shape = nshape, href = nhref, image =nimage)
    
    def get_node_label(self, node):
        return node
    
    def get_node_xlabel(self, node):
        return ''

    def get_node_shape(self, node):
        return 'plaintext'

    def get_node_href(self, node):
        return ''

    def get_node_image(self, node):
        return ''

    def set_graph_attr(self):
        self.G.graph_attr.update(layout = 'neato', rankdir='LR', concentrate = 'true', overlap = 'false', splines = 'true')


    def g(self):
        '''
        グラフを描写してHTMLに埋め込むメソッド
        '''
        return embed_dot(self.G.to_string())
    
    def df(self):
        '''
        データフレーム（表）に書き出すメソッド
        '''
        
        #ノードの属性（辞書になってる）を取り出してコラム名に設定する
        column_names = self.G.nodes()[0].attr.keys()

        df = pd.DataFrame(columns=column_names)

        for n in self.G.nodes():
            result_dict = OrderedDict()
            result_dict['node'] = n,
            for column_name in column_names:
                result_dict[column_name] = self.G.get_node(n).attr[column_name],

            df = df.append(pd.DataFrame(result_dict))
            
        df.index = range(1, len(df)+1) #最後にインデックスつけ
        return df

        


# ### Amazon商品情報による関連マップ 

# In[43]:

class AmazonRelateMap(RelateMap):
    
    title_dict = {}
    
    def get_start_node(self):
        items = item_search(self.keyword, item_page = 1)[:self.max_width]
        return [item.find('asin').text for item in items]
    
    def get_nextnodes(self, asin):
        '''
        asinを受けて類似本のasinのリストを返す
        '''
        items = item_search(asin, item_page = 1)
        result = []
        if items:
            item = items[0]
            self.title_dict[asin] = item.find('title').text
            for similarproduct  in item.findAll('similarproduct')[:self.max_width]:
                similar_asin = similarproduct.find('asin').text
                similar_title =  similarproduct.find('title').text
                self.title_dict[similar_asin] = similar_title
                result.append(similar_asin)
        return result

    def get_node_label(self, asin):
        return self.title_dict[asin]
    
    def get_node_href(self, asin):
        return 'http://www.amazon.co.jp/dp/' + str(asin)

    def set_graph_attr(self):
        self.G.graph_attr.update(layout = 'sfdp', rankdir='LR', concentrate = 'true', overlap = 'false', splines = 'true')

    def df(self):
        '''
        データフレーム（表）に書き出すメソッド
        '''
        
        #スーパークラスのメソッドをそのまま使う
        df = super(AmazonRelateMap, self).df()
        
        #カラム名をつけかえ
        df.columns = ['url', 'title', 'asin','shape']
        return df



# ### Amazon商品情報による関連マップ （商品画像付き）

# In[44]:

class AmazonPictureRelateMap(AmazonRelateMap):
        
    def image_download(self, asin, url):
        '''
        表紙イメージを (asin).jpgという名前でダウンロード
        '''
        with open(asin + '.jpg', "wb") as f:
            r = requests.get(url, headers=headers)
            f.write(r.content)
            
    def get_image_url(self, asin):
        items = item_search(asin, item_page = 1)
        if items and  items[0].find('largeimage'):
            return items[0].find('largeimage').find('url').text
        else:
            return ''
           
    def get_node_image(self, asin):
        url = self.get_image_url(asin)
        if url:
            self.image_download(asin, url)
            return asin + '.jpg'
        else:
            return ''

    def set_nodes_attr(self):
        for n in self.G.nodes():
            print '.',
            nlabel = self.get_node_label(n)
            nxlabel = self.get_node_xlabel(n)
            nshape = self.get_node_shape(n)
            nhref  = self.get_node_href(n)
            nimage  = self.get_node_image(n)
            if nimage:
                #self.G.add_node(n, label = nlabel, shape = nshape, href = nhref, image =nimage, labelloc='b')
                self.G.add_node(n, label = '', shape = nshape, href = nhref, image =nimage)
            else:
                self.G.add_node(n, label = nlabel, shape = nshape, href = nhref)
                
    def df(self):
        '''
        データフレーム（表）に書き出すメソッド
        '''
        
        #スーパークラスのメソッドをそのまま使う
        df = super(AmazonRelateMap, self).df()
        
        df['label'] = [self.title_dict[asin] for asin in df['node']]
        #カラム名をつけかえ
#         df.columns = ['url', 'title', 'asin','shape']
        return df



# ### コトバンク関連キーワードによる関連マップ

# In[45]:

class KotobankRelateMap(RelateMap):
    
    start_node = ''
    title_dict = dict()
    
    
    def get_start_node(self):
        self.start_node ='/word/' + urllib2.quote(self.keyword.encode('utf-8'))
        return self.start_node,
    
    def get_nextnodes(self, parturl):
        '''
        urlを受けて関連語のurlのリストを返す
        '''
        #print parturl
        result = []
        #url = 'https://kotobank.jp/word/%E7%B5%8C%E6%B8%88%E4%BA%88%E6%B8%AC-58788'
        r = requests.get('https://kotobank.jp' + parturl)
        tree = lxml.html.fromstring(r.content)
        
        this_title_tree = tree.xpath('//*[@id="mainTitle"]/h1/b')
        #print this_title_tree[0].text
        if this_title_tree:
             self.title_dict[parturl] = this_title_tree[0].text
        else:
            return None 
        
        links = tree.xpath('//*[@id="retailkeyword"]/a')
        for link in links:
            similar_title =  link.text           #予測
            similar_url =  link.attrib['href']  # /word/%E4%BA%88%E6%B8%AC-406123
            self.title_dict[similar_url] = similar_title
            result.append(similar_url)
        return result

    def get_node_href(self, parturl):
        return 'https://kotobank.jp' + parturl

    def get_node_label(self, parturl):
        return self.title_dict.get(parturl)
    
    def set_nodes_attr(self):
        super(KotobankRelateMap, self).set_nodes_attr()
        self.G.add_node(self.start_node, label = self.keyword, shape = 'circle')



# ### Weblio関連用語による関連マップ

# In[46]:

class WeblioRelateMap(RelateMap):
    
    start_node = ''
    title_dict = dict()
    
    def get_start_node(self):
        self.start_node ='http://www.weblio.jp/content/' + urllib2.quote(self.keyword.encode('utf-8'))
        return self.start_node,
    
    def get_nextnodes(self, url):
        '''
        urlを受けて関連語のurlのリストを返す
        '''
        #print url
        result = []
        # http://www.weblio.jp/content/%E4%BA%88%E6%B8%AC
        r = requests.get(url)
        tree = lxml.html.fromstring(r.content)
        
        this_title_tree = tree.xpath('//*[@id="topicWrp"]/span' )
        #print this_title_tree[0].text
        if this_title_tree:
             self.title_dict[url] = this_title_tree[0].text
        else:
            return None 
        
        links = tree.xpath('//div[@class="sideRWordsL"]/a')
        for link in links:
            similar_title =  link.text           #予測
            similar_url =  link.attrib['href']  
            self.title_dict[similar_url] = similar_title
            result.append(similar_url)
        return result

    def get_node_href(self, url):
        return url

    def get_node_label(self, url):
        return self.title_dict.get(url)

    def set_nodes_attr(self):
        super(WeblioRelateMap, self).set_nodes_attr()
        self.G.add_node(self.start_node, label = self.keyword, shape = 'circle')




# ## エクステンションで独自のマジックコマンドを定義

# In[47]:

#selectindexのための補助関数
def string2index(nowlist):
    resultlist = []
    for item in nowlist:
        item = item.strip()
        if item.isdigit():
            item = int(item)
            resultlist.append(item)
        else:
            if ':' in item:
                innrt_item = item.split(':')
                if innrt_item[0].isdigit() and innrt_item[1].isdigit():
                    item = range(int(innrt_item[0]), int(innrt_item[1])+1)
            resultlist.extend(item)
    return resultlist



from IPython.core.magic import (Magics, magics_class, line_magic,
                                cell_magic, line_cell_magic)

# The class MUST call this class decorator at creation time
@magics_class
class MyMagics(Magics):
    
    def line2value(self, line):
        now_user_namespace = self.shell.user_ns
        if line in now_user_namespace:
            return now_user_namespace[line]
        else:
            return line.encode('utf-8')
        
    def line2df(self, f, line):
        now_user_namespace = self.shell.user_ns
        if line in now_user_namespace:
            now_variable = now_user_namespace[line]
            if 'DataFrame' in str(type(now_variable)):
                return f(now_variable)
            else:
                return line + u' is not DataFrame, but ' +  str(type(now_variable))
        else:
            return line + u' is not defined.' 

    @line_magic
    def epwing(self, line):
        e =  epwing_info(self.line2value(line))
        df = e.collector()
        return df

    @line_magic
    def kotobank(self, line):
        k = Kotobank_info(self.line2value(line))
        df = k.collector()
        return df

    @line_magic
    def dictj(self, line):
        line = self.line2value(line)
        e = epwing_info(line)
        df = e.collector()
        df['url'] = '(epwing)'

        k = Kotobank_info(line)
        df = df.append(k.collector())

        w = Wikipedia_Info(line.decode('utf-8'), 'ja')
        df = df.append(w.fetch_page())

        df = df.sort_values(by='des_size') #並べ替え
        df.index = range(1, len(df)+1) #最後にインデックスつけ
        return df

    
    
    @line_magic
    def encyclopediacom(self, line):
        k = encyclopediacom_info(self.line2value(line))
        df = k.collector()
        return df

    #en English
    @line_magic
    def wikipedia_e(self, line):
        w = Wikipedia_Info(unicode(self.line2value(line)),'en')
        return w.fetch_page()

    #simple Simple English
    @line_magic
    def wikipedia_s(self, line):
        w = Wikipedia_Info(unicode(self.line2value(line)),'simple')
        return w.fetch_page()

    #de Deutsch
    @line_magic
    def wikipedia_de(self, line):
        w = Wikipedia_Info(unicode(self.line2value(line)),'de')
        return w.fetch_page()

    #fr français
    @line_magic
    def wikipedia_fr(self, line):
        w = Wikipedia_Info(unicode(self.line2value(line)),'fr')
        return w.fetch_page()

    #es español
    @line_magic
    def wikipedia_es(self, line):
        w = Wikipedia_Info(unicode(self.line2value(line)),'es')
        return w.fetch_page()

    #ru русский
    @line_magic
    def wikipedia_fr(self, line):
        w = Wikipedia_Info(unicode(self.line2value(line)),'ru')
        return w.fetch_page()

    @line_magic
    def wikipedia_j(self, line):
        w = Wikipedia_Info(self.line2value(line).decode('utf-8'),'ja')
        return w.fetch_page()

    @line_magic
    def ndl(self, line):
        w = ndl_list_info(self.line2value(line).decode('utf-8'))
        df = w.collector()
        return df

    @line_magic
    def cinii_list(self, line):
        w = CiNii_list_info(self.line2value(line))
        df = w.collector()
        return df

    @line_magic
    def webcat(self, line):
        w = webcat_list_info(self.line2value(line))
        df = w.collector()
        return df

    @line_magic
    def worldcat(self, line):
        w = Worldcat_list_info(self.line2value(line))
        df = w.collector()
        return df

    @line_magic
    def r_list(self, line):
        r = refcases_list_info(self.line2value(line).decode('utf-8'))
        df = r.collector()
        return df

    @line_magic
    def refcase(self, line):
        '''
        レファレンス協同データベースを検索して、データフレームを返す

        書式：
        %refcase (keyword),[num]
        
                keyword:検索語（必須）
                num: 最大表示件数（デフォルト10件）

        例：角倉了以に関するレファレンス事例を１０件分表示する
        %refcase　角倉了以

        例：角倉了以に関するレファレンス事例を5件分表示する
        %refcase　角倉了以,5

        '''

        line_items = self.line2valuelist(line)
        if len(line_items) > 1:
            now_max_num = int(line_items[1])
        else:
            now_max_num = 10

        r = Refcases_info(line_items[0].decode('utf-8'), now_max_num)
        df = r.collector()
        df = pd.concat([df.ix[:,5:12], df.ix[:,20:21]], axis=1)
        return df    

    

    @line_magic
    def eb(self, line):
        '''
        データフレームを全件表示、URLはリンクかしてHTMLに埋め込んで表示

        書式：
        %eb df

        例：直近の結果であるデータフレームを埋め込む
        %eb _　

        例：Out[3]の結果であるデータフレームを埋め込む
        %eb _3

        '''
        return self.line2df(embed_df, line)
    
    @line_magic
    def html2df(self, line):
        '''
        HTMLに埋め込んだデータからデータフレームに変換する
        '''
        now_user_namespace = self.shell.user_ns
        if line in now_user_namespace:
            now_variable = now_user_namespace[line]
            if 'IPython.core.display.HTML' in str(type(now_variable)):
                return pd.read_html(StringIO(now_variable.data), index_col =0, header=0)[0]
            else:
                return line + u' is not HTML, but ' +  str(type(now_variable))
        else:
            return line + u' is not defined.' 



    #書誌データフレームの目次を複数の列に展開する
    @line_magic
    def expand_content(self,line):
        '''
        データフレームに含まれる目次項目を展開する

        書式：
        %exp_cont df

        例：直近の結果であるデータフレームに含まれる目次項目を展開する
        %exp_cont _　

        例：Out[3]の結果であるデータフレームに含まれる目次項目を展開する
        %exp_cont _3

        '''
        now_user_namespace = self.shell.user_ns
        if line in now_user_namespace:
            df = now_user_namespace[line]
            if 'DataFrame' in str(type(df)):
                if 'contents' in df.columns:
                    split_contents_df = df['contents'].str.split('\t', n=0, expand=True).fillna(value='')
                    return pd.concat([df[['title','summary']], split_contents_df],axis=1)
                else:
                    return df
            else:
                print line, 'is not DataFrame, but ', type(now_variable)
        
    @line_magic
    def extbook(self, line):
        '''
        データフレームに含まれる書名（『書名』こういう形式のもの）を抜き出してデータフレームにして返す

        書式：
        %extbook df

        例：直近の結果であるデータフレームに含まれる書名を抜き出してデータフレームに
        %extbook _　

        例：Out[3]の結果であるデータフレームに含まれる書名を抜き出してデータフレームに
        %extbook _3

        '''
        now_user_namespace = self.shell.user_ns
        if line in now_user_namespace:
            now_variable = now_user_namespace[line]
            if 'DataFrame' in str(type(now_variable)):
                return ext_book(now_variable)
            else:
                print line, 'is not DataFrame, but ', type(now_variable)

    @line_magic
    def amazonreviews(self, line):
        '''
        isbnが含まれるデータフレームを受け取り、アマゾンレビューのデータフレームを返す

        書式：
        %reviews df

        例：直近の結果であるデータフレームからisbnを受け取りアマゾンレビューのデータフレームを返す
        %reviews _　

        例：Out[3]の結果であるデータフレームからisbnを受け取りアマゾンレビューのデータフレームを返す
        %reviews _3

        '''
        now_user_namespace = self.shell.user_ns
        if line in now_user_namespace:
            now_variable = now_user_namespace[line]
            if 'DataFrame' in str(type(now_variable)):
                a = amazon_reviews(now_variable)
                return a.collector()
            else:
                print line, 'is not DataFrame, but ', type(now_variable)
            
                
    @line_magic
    def stocks_amazon(self, line):
        '''
        書誌データフレームを受け、アマゾンの在庫と最安値の一覧表をデータフレームで返す

        返り値：DataFrame

        書式：　%stocks_amazon biblio_df ……

        例：out[1]の書誌データフレームに出てくる本を探しアマゾンの在庫と最安値の一覧表をデータフレームで返す


         %stocks_amazon _1

        '''    
        now_user_namespace = self.shell.user_ns
        if line in now_user_namespace:
            now_variable = now_user_namespace[line]
            if 'DataFrame' in str(type(now_variable)):
                return amazon_stocks(now_variable)
            else:
                print line, 'is not DataFrame, but ', type(now_variable)


    @line_magic
    def stocks_kosho(self, line):        
        '''
        書誌データフレームを受け、『日本の古本屋』に出品している書籍、出品店、値段などをデータフレームで返す

        返り値：DataFrame

        書式：　%stocks_amazon biblio_df ……

        例：out[1]の書誌データフレームに出てくる本を探し出品している書籍、出品店、値段などをデータフレームで返す

         %stocks_kosho _1

        '''    
        now_user_namespace = self.shell.user_ns
        if line in now_user_namespace:
            now_variable = now_user_namespace[line]
            if 'DataFrame' in str(type(now_variable)):
                return kosho_stocks(now_variable)
            else:
                print line, 'is not DataFrame, but ', type(now_variable)


    @line_magic
    def stocks_ndl(self, line):
        '''
        書誌データフレームを受け、
        国会図書館、各県立図書館の所蔵／貸し出し状況／予約URLについてデータフレームにまとめて返す

        返り値：DataFrame

        書式：　%stocks_ndl biblio_df 

        例：out[1]の書誌データフレームに出てくる本を探し
          国会図書館、各県立図書館の所蔵／貸し出し状況／予約URLについてデータフレームにまとめて返す

         %stocks_ndl _1

        '''    
        now_user_namespace = self.shell.user_ns
        if line in now_user_namespace:
            now_variable = now_user_namespace[line]
            if 'DataFrame' in str(type(now_variable)):
                return ndl_stocks(now_variable)
            else:
                print line, 'is not DataFrame, but ', type(now_variable)



    @line_magic
    def ndlcollection(self, line):
        '''
        書誌データフレームを受け、
        国会図書館デジタルコレクション、国会図書館複写サービス、外部リポジトリCiNii, JAIRO等へのリンク
        をまとめた表をデータフレームで返す

        返り値：DataFrame

        書式：　%ndlcollection biblio_df 

        例：out[1]の書誌データフレームに出てくる本を探し
          デジタルコレクション、国会図書館複写サービス、外部リポジトリCiNii, JAIRO等へのリンク
                をまとめた表をデータフレームで返す


         %ndlcollection _1

        '''    
        now_user_namespace = self.shell.user_ns
        if line in now_user_namespace:
            now_variable = now_user_namespace[line]
            if 'DataFrame' in str(type(now_variable)):
                return ndl_collection(now_variable)
            else:
                print line, 'is not DataFrame, but ', type(now_variable)
    
        
    @line_magic
    def librarystatus(self, line):
        '''
        isbnを含むbiblioデータフレームと図書館リストのデータフレームを渡して、
        isbn、タイトル、所蔵／貸し出し状況／予約URLについてデータフレームにまとめて返す

        返り値：DataFrame

        書式：　%librarystatus biblio_df, library_df
         biblio_df　%makebibでできるi書誌情報のデータフレーム
         library_df　%librarylistでできる図書館リストのデータフレーム（デフォルトはMYLIBRARY)

        例：Out[1],Out[3],Out[7]のブックリストをまとめてデータフレームb_dfをつくり、
          「淀屋橋駅」付近の図書館の所蔵／貸し出し状況／予約URLのデータフレームをつくる

        b_df = %makebib _1,  _3, _7
         l_df = %librarylist 淀屋橋駅
         %librarystatus b_df, l_df

        '''    

        now_user_namespace = self.shell.user_ns
        if len(line.split(',')) == 2:
            bib_df_name = line.split(',')[0].strip()
            lib_df_name = line.split(',')[1].strip()
            if bib_df_name in now_user_namespace.keys() and lib_df_name in now_user_namespace.keys():
                bib_df = now_user_namespace[bib_df_name]
                lib_df = now_user_namespace[lib_df_name]
                if 'DataFrame' in str(type(bib_df)) and 'DataFrame' in str(type(lib_df)):
                    return library_status(bib_df, lib_df)
                else:
                    print 'not DataFrame'
                    return
            else:
                print item, 'not defined.'
                return
        elif len(line.split(',')) == 1:
            bib_df_name = line.split(',')[0].strip()
            if bib_df_name in now_user_namespace.keys():
                bib_df = now_user_namespace[bib_df_name]
                if 'DataFrame' in str(type(bib_df)):
                    return library_status(bib_df)
                else:
                    print 'not DataFrame'
                    return
            else:
                print item, 'not defined.'
                return
            


    #選択系ツール

    @line_magic
    def selectstr(self, line):
        '''
        与えたデータフレームから、コラム名で指定した列（コラム／フィールド）に検索文字列が含まれるものを抜き出す

        返り値：DataFrame

        書式：
        %selectstr DataFrame, column_name, search_string

         DataFrame　データフレーム
         column_name　コラム（フィールド）
         search_string　検索文字列


        例：直近の出力結果（データフレーム）から、titleフィールドに「文化祭」が含まれているものを抜き出す
        %selectstr _,　title, 文化祭

        '''
        now_user_namespace = self.shell.user_ns
        df_name = line.split(',')[0].strip()
        column_name = line.split(',')[1].strip()
        search_string = line.split(',')[2].strip()
        
        if df_name in now_user_namespace.keys():
            df = now_user_namespace[df_name]
            if 'DataFrame' in str(type(df)):
                    return df[df[column_name].str.contains(search_string)]
            else:
                print df_name, 'is not DataFrame, but ', type(df)
                return
        else:
            print df_name, 'is not defined.'
            return

        
    
    @line_magic
    def selectcolumn(self, line):
        '''
        与えたデータフレームから、コラム名で指定した列（コラム／フィールド）を抜き出す

        返り値：DataFrame

        書式
        %selectcolumn DataFrame, column_name1, column_name2, column_name3, ....
            DataFrame　データフレーム
         column_name1　コラム名その１
         column_name2　コラム名その２
           ……

        例：直近の結果（データフレーム）から「title」「summary」「contents」の列を抜き出す
        %selectcolumn _94, 'title','summary','contents'

        '''
        now_user_namespace = self.shell.user_ns
        df_name = line.split(',')[0].strip()
        column_names = line.split(',')[1:]
        select_columns = [col.strip() for col in column_names]
        
        if df_name in now_user_namespace.keys():
            df = now_user_namespace[df_name]
            if 'DataFrame' in str(type(df)):
                    return df[select_columns]
            else:
                print df_name, 'is not DataFrame, but ', type(df)
                return
        else:
            print df_name, 'is not defined.'
            return

    @line_magic
    def selectindex(self, line):
        '''
        与えたデータフレームから、index番号で指定された行を抜き出す

        返り値：DataFrame

        書式
        %selectindex DataFrame, index_num1, index_num2, ....
            DataFrame　データフレーム
         index_num1　index番号その１
         index_num2　index番号その２
           ……

        例：直近の結果（データフレーム）から1,4〜7,10行目を抜き出す
        %selectcol _94, 1,4:7,10

        '''
        now_user_namespace = self.shell.user_ns
        df_name = line.split(',')[0].strip()
        index_names = line.split(',')[1:]
        #select_indexs = [int(idx) for idx in index_names]
        select_indexs = string2index(index_names)
        
        #print select_indexs
        if df_name in now_user_namespace.keys():
            df = now_user_namespace[df_name]
            if 'DataFrame' in str(type(df)):
                    return df.query("index == {}".format(select_indexs))
            else:
                print df_name, 'is not DataFrame, but ', type(df)
                return
        else:
            print df_name, 'is not defined.'
            return


        
    
    @line_magic
    def makebib(self, line):
        '''
        ブックリスト系のデータフレームを複数受け重複を除き、webcat詳細ページから得た情報で書誌データフレームを完成させる

        返り値：DataFrame

        書式：　%makebib df1, df2, df3, ……

        例：out[1]とout[3]とout[7]の書誌情報（isbn, webcatのurl、titleなど）を含むデータフレームを統合し
          書誌データフレームを完成させる

         %makebib _1,  _3, _7

        '''    
        now_user_namespace = self.shell.user_ns
        #print list(now_user_namespace.keys())
        now_list = []
        for item in line.split(','):
            item = item.strip()
            if item in now_user_namespace.keys():
                now_variable = now_user_namespace[item]
                if 'DataFrame' in str(type(now_variable)):
                    now_list.append(now_variable)
                else:
                    print item, 'is not DataFrame, but ', type(now_variable)
                    return
            else:
                    print item, 'is not defined.'
                    return
        #print type(now_list)
        return make_biblio(now_list)

    @line_magic
    def concatdf(self, line):
        '''
        データフレームを複数受けて、マージする

        返り値：DataFrame

        書式：　%margedf df1, df2, df3, ……

        '''    
        now_user_namespace = self.shell.user_ns
        #print list(now_user_namespace.keys())
        now_list = []
        for item in line.split(','):
            item = item.strip()
            if item in now_user_namespace.keys():
                now_variable = now_user_namespace[item]
                if 'DataFrame' in str(type(now_variable)):
                    now_list.append(now_variable)
                else:
                    print item, 'is not DataFrame, but ', type(now_variable)
                    return
            else:
                    print item, 'is not defined.'
                    return
        #print type(now_list)
        return pd.concat(now_list)


    @line_magic
    def df2csv(self, line):
        '''
        データフレームをcsvに変換する
        '''    
        now_user_namespace = self.shell.user_ns
        if line in now_user_namespace:
            now_variable = now_user_namespace[line]
            if 'DataFrame' in str(type(now_variable)):
                output = cStringIO.StringIO()
                now_variable.to_csv(output, index=False, encoding='utf-8')
                print output.getvalue()
                return output.getvalue().decode('utf-8')
            else:
                print line, 'is not DataFrame, but ', type(now_variable)

    @line_magic
    def kosho(self, line):
        k = Kosho_info(self.line2value(line))
        df = k.collector()
        return df

    @line_magic
    def koshotitle(self, line):
        k = Kosho_info_title(self.line2value(line))
        df = k.collector()
        return df

    @line_magic
    def google(self, line):
        w = Google_info(self.line2value(line).decode('utf-8'))
        df = w.collector()
        return df

    @line_magic
    def googlebook(self, line):
        w = Google_book_info(self.line2value(line).decode('utf-8'))
        df = w.collector()
        return df

    @line_magic
    def thememap(self, line):
        '''
        WIkipediaのカテゴリー情報をつかってテーママップ（概念階層図）を描く

        書式：%thememap keyword 

        例：　　　%suggestmap 深層学習
        '''
        m = Thememap(self.line2value(line))
        g = m.draw()
        return embed_dot(g)

    @line_magic
    def suggestmap(self, line):
        '''
        googleサジェストをつかって検索語の共起語を得てマップを描く

        書式：
        %suggestmap keyword [,1 or 2]


        例：ノーマルモードで検索語の共起語を得てマップを描く
        %suggestmap 深層学習

        例：エキスパンドモードでより網羅的に検索語の共起語を得てマップを描く
        %suggestmap 深層学習,1

        例：スーパーモードでさらに網羅的に検索語の共起語を得てマップを描く
        %suggestmap 深層学習,2

        '''

        split_line = line.split(',')
        if len(split_line) == 1:
            print 'normal mode'
            m = SuggestMap(unicode(self.line2value(line).decode('utf-8')),0)
            g = m.draw()
            return embed_dot(g)
        elif len(split_line) == 2 and split_line[1]  in  u'1':
            print 'expand mode'
            m = SuggestMap(unicode(self.line2value(split_line[0]).decode('utf-8')),1)
            g = m.draw()
            return embed_dot(g)
        elif len(split_line) == 2 and split_line[1] in  u'2':
            print 'super mode'
            m = SuggestMap(unicode(self.line2value(split_line[0]).decode('utf-8')),2)
            g = m.draw()
            return embed_dot(g)
        else:
            print 'mode error - see %suggestmap?'

            
    def line2valuelist(self, lines):
        return [self.line2value(line) for line in lines.split(',')]

    @line_magic
    def wikipedia(self, line):
        '''
        言語を指定してWikipediaを検索する

        書式：
        %wikipedia keyword, langueage
        
        keyword: 検索語（必須）
        langueage :　言語指定（ja, en, de, ...)
        
        '''
        line_items = self.line2valuelist(line)
        #print line_items
        keyword = line_items[0].strip()
        language = line_items[1].strip()
        print keyword, language
        w = Wikipedia_Info(keyword.decode('utf-8'), language)
        return w.fetch_page()

    @line_magic
    def amazonmap(self, line):
        '''
        Amazon Product Advertising APIを使って関連商品(Similarities)の関連図をつくる

        書式：
        %amazonmap keyword, depth, start_num

        keyword: 検索語（必須）
        depth: 探索の深さ（デフォルト値 2）
        width: 探索の広がり （デフォルト値 5）

        使用例
        %amazonmap 文化祭企画

        %amazonmap 深層学習, 3, 3
        '''

        line_items = self.line2valuelist(line)
        if len(line_items) > 1:
            now_max_level = int(line_items[1])
        else:
            now_max_level = 1
        if len(line_items) > 2:
            now_start_num= int(line_items[2])
        else:
            now_start_num = 5
        return AmazonRelateMap(unicode(line_items[0]), max_depth=now_max_level, max_width = now_start_num)
            
    @line_magic
    def amazonPmap(self, line):
        '''
        Amazon Product Advertising APIを使って関連商品(Similarities)の関連図（表紙画像）をつくる

        書式：
        %amazonmap keyword, depth, start_num

        keyword: 検索語（必須）
        depth: 探索の深さ（デフォルト値 2）
        width: 探索の広がり （デフォルト値 5）

        使用例
        %amazonPmap 文化祭企画

        %amazonPmap 深層学習, 3, 3
        '''

        line_items = self.line2valuelist(line)
        if len(line_items) > 1:
            now_max_level = int(line_items[1])
        else:
            now_max_level = 2
        if len(line_items) > 2:
            now_start_num= int(line_items[2])
        else:
            now_start_num = 5
        return AmazonPictureRelateMap(unicode(line_items[0]), max_depth=now_max_level, max_width = now_start_num)

    @line_magic
    def kotobankmap(self, line):
        '''
        kotobankの関連キーワードをつかって関連図をつくる

        書式：
        %kotobankmap keyword, depth

        keyword: 検索語（必須）
        depth: 探索の深さ（デフォルト値 2）

        使用例
        %kotobankmap 文化祭企画

        %kotobankmap 深層学習, 2
        '''

        line_items = self.line2valuelist(line)
        if len(line_items) > 1:
            now_max_level = int(line_items[1])
        else:
            now_max_level = 2
        print line_items[0],type(line_items[0])
        k = KotobankRelateMap(unicode(line_items[0].decode('utf-8')), max_depth=now_max_level, max_width = 0)
        return k.g()

    @line_magic
    def webliomap(self, line):
        '''
        Weblioの関連キーワードをつかって関連図をつくる

        書式：
        %webliomap keyword, depth

        keyword: 検索語（必須）
        depth: 探索の深さ（デフォルト値 2）

        使用例
        %webliomap 文化祭企画

        %webliomap 深層学習, 3
        '''

        line_items = self.line2valuelist(line)
        if len(line_items) > 1:
            now_max_level = int(line_items[1])
        else:
            now_max_level = 2
        w = WeblioRelateMap(unicode(line_items[0].decode('utf-8')), max_depth=now_max_level, max_width = 0)
        return w.g()

    @line_magic
    def librarylist(self, line):
        '''
        地名のリストを渡して付近の図書館のリスト（館名、住所、電話、geocode、URLなど）のデータフレームを返す

        返り値：DataFrame

        書式
        %librarylist  address1, address2, address3, ....
            DataFrame　データフレーム
         index_number1　行(index)番号その１
         index_number2　行(index)番号その２
           ……

        例：立ち寄り先３箇所（京都市北区 大阪市西区 神戸市中央区）の付近の
          図書館のリスト（館名、住所、電話、geocode、URLなど）のデータフレームを返す

        %librarylist 京都市北区, 大阪市西区, 神戸市中央区


        '''
        now_list = self.line2valuelist(line)
        return library_list([i.decode('utf-8') for i in now_list])
 
    @line_magic
    def extamazon(self, line):
        '''
        urlで指定されるページからamazon.co.jpへのリンクを抽出してtitle, asinのデータフレームを返す
        '''
        return ext_amazon(self.line2value(line))

    @line_magic
    def interlang(self, line):
        '''
        wikipediaの「他の言語へのリンク」を使って各語の訳語をデータフレームで返す
        '''
        return interlanguage(self.line2value(line))


#     @line_magic
#     def lmagic(self, line):
#         "my line magic"
#         print("Full access to the main IPython object:", self.shell)
#         print("Variables in the user namespace:", list(self.shell.user_ns.keys()))
#         return line       
# In order to actually use these magics, you must register them with a
# running IPython.  This code must be placed in a file that is loaded once
# IPython is up and running:                
ip = get_ipython()
# You can register the class itself without instantiating it.  IPython will
# call the default constructor on it.
ip.register_magics(MyMagics)

#ここで登録したマジックコマンドは、load_ipython_extensionしなくていい


# In[48]:

def load_ipython_extension(ipython):
    ipython.register_magic_function(text2bib, 'cell')
    ipython.register_magic_function(csv2df, 'cell')    
    ipython.register_magic_function(csv2dot, 'cell')    
    ipython.register_magic_function(indent2dot, 'cell')

