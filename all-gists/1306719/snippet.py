from html.parser import HTMLParser
from urllib import request

import os.path
import re
import json
import sys

class ImgListScraper( HTMLParser ):

    IMG_URL = "http://i.imgur.com/{hash}{ext}"

    def __init__( self, *args, **kwargs ):
        super().__init__( *args, **kwargs )
        self.in_javascript = False
        self.data = None

    def handle_starttag( self, tag, attrs ):

        attrs = dict( attrs )

        if tag == "script" and attrs['type'] == "text/javascript":
            self.in_javascript = True

    def handle_data( self, data ):

        if self.in_javascript:

            img_block = False
            for line in data.splitlines():

                if line.find("ImgurAlbum") > -1:
                    img_block = True
                elif img_block and line.strip().startswith("images:"):
                    data = line.strip()[ len( "images: " ) : -1 ]
                    self.data = json.loads( data )
                    img_block = False

            self.in_javascript = False

    def img_urls( self ):
        for image in self.data['items']:
            yield self.IMG_URL.format( **{
                    'hash': image['hash'],
                    'ext': image['ext']
                    })

def download_image( url, folder ):

    path = os.path.join( folder, url.split("/")[-1] )
    res = request.urlopen( url )

    with open( path, 'wb' ) as f:
        f.write( res.read() )

    res.close()

def download_album( album_url, folder ):

    print( "Scraping album..." )
    scraper = ImgListScraper()
    html = request.urlopen( album_url ).read().decode( 'utf8' )
    scraper.feed( html )

    total = scraper.data['count']

    for ( pos, img_url ) in enumerate( scraper.img_urls() ):

        print( "downloading {img_url} ({pos} of {total})".format( 
            img_url = img_url,
            pos = pos,
            total = total ) )

        download_image( img_url, folder )

if __name__ == '__main__':

    if len( sys.argv ) < 3:
        print( "Usage: {script} ALBUM_URL FOLDER".format( script = sys.argv[0]
            ) )
    else:
        download_album( sys.argv[1], sys.argv[2] )
