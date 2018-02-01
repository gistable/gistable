from pyquery import PyQuery as pq
import requests
import psycopg2 as pg

def get_title(element):
    return element.cssselect('.media-heading a')[0].text


def get_rating(element):
    el = element.cssselect("div[style='color:#F1870A']")[0]
    rating = len(el.cssselect('.glyphicon-star'))
    if el.text_content()[-1] == '½':
        rating += 0.5
    return rating


def get_release_year(element):
    return int(element.cssselect('.media-heading .subtle')[0].text.strip('()'))


def get_movies(page):
    return page('#main_container .media-body')


def main():
    ratings = {}
    url = 'https://www.rottentomatoes.com/user/id/906460927/ratings'
    print('Getting data from RT...')
    request = requests.get(url)
    page = pq(request.text)
    for movie in get_movies(page):
        title = get_title(movie)
        if title not in ratings:
            ratings[title] = [get_rating(movie), get_release_year(movie)]
    print('Storing data into postgres...')
    conn = pg.connect('dbname=movies')
    cur = conn.cursor()
    for rating in ratings:
        cur.execute('INSERT INTO ratings (title, rating, release_year) VALUES (%s, %s, %s);',
                    (rating, ratings[rating][0], ratings[rating][1]))
    conn.commit()
    cur.close()
    conn.close()
    print("Done!")


if __name__ == '__main__':
    main()