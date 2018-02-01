import requests, bs4, os
from lxml import html

page_num = 5
username = 'XXX@XXX.com'
password = 'AAABBBCCC'

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; '
                  'Intel Mac OS X 10_11_2) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/47.0.2526.111 Safari/537.36'
}

session = requests.Session()

response = session.get('https://www.tumblr.com/login')
r = html.fromstring(response.text)
form_key1 = r.xpath("//meta[@id='tumblr_form_key']/@content")[0]
form_key2 = r.xpath("//input[@name='form_key']")[0].value

payload = {
    'user[email]': username,
    'user[password]': password,
    'tumblelog[name]': '',
    'user[age]': '',
    'context': 'other',
    'version': 'STANDARD',
    'follow': '',
    'http_referer': 'https://www.tumblr.com/',
    'form_key': form_key1,
    'seen_suggestion': '0',
    'used_suggestion': '0',
    'used_auto_suggestion': '0',
    'about_tumblr_slide': '',
    'random_username_suggestions': '["DarkGlitterCollective", "ShinyCrusadeWolf", "ZanyStrawberryGlitter", "HerPainterNacho","TenderlySpookyFlower"]',
}

session.post('https://www.tumblr.com/login', headers=headers, data=payload)

page = session.get('https://www.tumblr.com/dashboard')
soup = bs4.BeautifulSoup(page.text, features='html5lib')

for j in range(0, page_num):

    for i in soup.select('.post_media_photo'):
        # download every image in the post list
        print(i.get('width'), i.get('height'), i.get('src'))

        try:
            img_url = i.get('src')
            # Download the image.
            print('Downloading image %s...' % (img_url))
            res = requests.get(img_url)
            res.raise_for_status()
        except requests.exceptions.MissingSchema:
            # skip this image
            continue

        try:
            # make folder for every page
            folder = os.path.join('tumblr', str(j))
            os.makedirs(folder, exist_ok=True)

            print('Saving image:', folder, os.path.basename(img_url))

            imageFile = open(os.path.join(folder, os.path.basename(img_url)), 'wb')
        except FileExistsError:
            continue

        for chunk in res.iter_content():
            imageFile.write(chunk)

        imageFile.close()

    # get next page
    next_page_link = 'https://www.tumblr.com' + soup.select('#next_page_link')[0].get('href')
    page = session.get(next_page_link)
    soup = bs4.BeautifulSoup(page.text, features='html5lib')
