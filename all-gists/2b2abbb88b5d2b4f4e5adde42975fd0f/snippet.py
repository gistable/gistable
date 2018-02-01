from bs4 import BeautifulSoup
import requests, csv, os
from newspaper import Article
from time import gmtime, strftime

#create folder
identifier = str(strftime("%Y-%m-%d %H-%M-%S", gmtime()))
os.makedirs('C:\\Users\\person\\folder\\more_folders\\final_folder\\' + identifier)

#beautiful soup stuff - change url to search term
url = 'http://search.abc.net.au/s/search.html?query=%22hit+and+run%22&collection=news_meta&form=simple&gscope1=10'
res = requests.get(url)
soup = BeautifulSoup(res.text, 'html.parser')

#lists of things
links_titles = []
links = []
titles = []
dates = []
iterator_list = []


#determine amount of results for search term
soup_results = str(soup.find('p', 'fb-result-count'))
results_mash = soup_results.split(' ')
results = results_mash[4].replace(',', '')

print('Currently processing results for \n%s...' % url)

#determine amount of pages for search term
pages = int(results) // 10 + 1
print('No. of Pages: %s\nTotal Results: %s' % (pages, results))

#create list of result pages containing 10 links each
print('Creating list of results pages...')
results_no = 11
iterator_list.append(url)
for i in range(pages-1):
    link = url + '&start_rank=' + str(results_no)
    iterator_list.append(link)
    results_no += 10
print('Finished creating list of results pages.')

#iterate through pages of results, collate links, titles, dates, in to lists
print('Pulling dates, links, and titles from each of the %s results pages...' % pages)
for i in range(pages):
    local_url = iterator_list[i]
    local_res = requests.get(local_url)
    local_soup = BeautifulSoup(local_res.text, 'html.parser')
    soup_a = local_soup.find_all('a')
    links_titles = soup_a[31:41]
    for i in range(len(links_titles)):
        try:
            data = str(links_titles[i])
            mash = data.split('"')
            link = mash[1]
            links.append(link)
            title = mash[4].replace('<strong>', '').replace('</strong>', '') \
                .replace('</a>', '').replace('>', '').strip()
            titles.append(title)
        except IndexError: #why does this need to be here? i don't know
            break
    datemash = local_soup.find_all('span', 'fb-date')
    for i in range(len(datemash)):
        data = str(datemash[i])
        date = data.replace('<span class="fb-date">', '').replace('</span>', '').replace(' ', '-')
        dates.append(date)
print('Data successfully scraped from %s pages.' % pages)

#saving articles - change path to folder (folder must end with \\)
print('Downloading %s articles. This stage will take some time.\nProgress can be checked in the destination folder.' % results)
print('Errors:')
for i in range(len(links)):
    article_link = links[i]
    try:
        filename = i+1
        article = Article(article_link)
        article.download()
        article.parse()
        file = open('C:\\Users\\person\\folder\\more_folders\\final_folder\\' + identifier + '\\' + str(filename) + '.txt', 'w')
        file.write('%s\n' %(dates[i]))
        file.write(article.text)
    except Exception as e:
        print('Error in article %s, link %s, error: %s' %((i+1), links[i], str(e)))
print('Downloading of %s articles complete.' % results)

#change path to name of CSV to be created
print('Creating .csv of links, titles, dates...')
with open('C:\\Users\\person\\folder\\more_folders\\final_folder\\' + identifier + '\\' + 'data.csv', 'wt', newline = '') as f:
   writer = csv.writer(f)
   rows = zip(dates, titles, links)
   for row in rows:
       writer.writerow(row)

print('Data.csv successfully created.\nWeb scrape finished.')