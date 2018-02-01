#!/usr/bin/env python3

import csv
import urllib.request

from bs4 import BeautifulSoup


BASE_URL = 'http://www.weblancer.net/projects/'


def get_html(url):
    response = urllib.request.urlopen(url)
    return response.read()


def get_page_count(html):
    soup = BeautifulSoup(html)
    paggination = soup.find('div', class_='pages_list text_box')
    return int(paggination.find_all('a')[-2].text)


def parse(html):
    soup = BeautifulSoup(html)
    table = soup.find('table', class_='items_list')
    rows = table.find_all('tr')[1:]

    projects = []
    for row in rows:

        cols = row.find_all('td')

        projects.append({
            'title': cols[0].a.text,
            'categories': [category.text for category in cols[0].find_all('noindex')],
            'price': cols[1].text.strip().split()[0],
            'application': cols[2].text.split()[0]
        })

    return projects

def save(projects, path):
    with open(path, 'w') as csvfile:
        writer = csv.writer(csvfile)

        writer.writerow(('Проект', 'Категории', 'Цена', 'Заявки'))

        writer.writerows(
            (project['title'], ', '.join(project['categories']), project['price'], project['application']) for project in projects
        )

def main():
    total_pages = get_page_count(get_html(BASE_URL))

    print('Всего найдено %d страниц...' % total_pages)

    projects = []

    for page in range(1, total_pages + 1):
        print('Парсинг %d%% (%d/%d)' % (page / total_pages * 100, page, total_pages))
        projects.extend(parse(get_html(BASE_URL + "page=%d" % page)))

    print('Сохранение...')
    save(projects, 'projects.csv')


if __name__ == '__main__':
    main()