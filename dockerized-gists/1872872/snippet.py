#!/usr/bin/env python

'''
This script originated at http://pastebin.com/zK3ZYaS8
I've modified it... just a `little` bit. ;P
I only reached to page 161 and Twitter stopped giving me
tweets. :( Let me know if you get further!

                                    - Mike Helmick

Account you are scraping MUST not be protected. ;)

Before running, be sure you have BeautifulSoup
`pip install BeautifulSoup`
'''

import time
from urllib2 import urlopen
try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    raise ImportError('Goober, be sure to have BeautifulSoup installed.')

user = 'mikehelmick'  # Replace with your twitter username
url = u'http://twitter.com/%s?page=' % (user)
tweets_file = open('tweets-%s.html' % user, 'w')

html_head = '''
<!DOCTYPE html>
<html lang="en">
    <head>
      <meta charset="utf-8">
      <title>%(user)s Tweets</title>
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <meta name="description" content="">
      <meta name="author" content="">

      <!-- Le styles -->
      <link href="http://twitter.github.com/bootstrap/assets/css/bootstrap.css" rel="stylesheet">
      <style type="text/css">
            body {
              padding-top: 60px;
              padding-bottom: 40px;
            }

            #timeline{
                -webkit-border-radius: 4px;
                   -moz-border-radius: 4px;
                        border-radius: 4px;
                border-top: 1px solid #eee;
                border-right: 1px solid #eee;
                border-left: 1px solid #eee;
                margin:0 !important;
            }

                #timeline li{
                    list-style:none;
                    padding:12px 6px;
                    border-bottom:1px solid #eee;
                }

            .retweet-meta, .entry-meta{
                display:block;
                font-size:11px;
                padding: 4px;
            }

            .entry-meta{
                background: #D9EDF7;
            }

            .retweet-meta{
                background: #DFF0D8;
                color: #468847;
                margin-top:2px;
            }
      </style>
      <link href="http://twitter.github.com/bootstrap/assets/css/bootstrap-responsive.css" rel="stylesheet">

      <!-- Le HTML5 shim, for IE6-8 support of HTML5 elements -->
      <!--[if lt IE 9]>
        <script src="//html5shim.googlecode.com/svn/trunk/html5.js"></script>
      <![endif]-->
    </head>

    <body>
    <div class="navbar navbar-fixed-top">
        <div class="navbar-inner">
            <div class="container">
                <a class="btn btn-navbar" data-toggle="collapse" data-target=".nav-collapse">
                    <span class="icon-bar"></span>
                    <span class="icon-bar"></span>
                    <span class="icon-bar"></span>
                </a>
                <a class="brand" href="#">%(user)s Tweets</a>
                <div class="nav-collapse">
                  <ul class="nav">
                    <li class="active"><a href="#">Home</a></li>
                  </ul>
                </div><!--/.nav-collapse -->
            </div>
        </div>
    </div>

    <div class="container">
        <div class="row">
            <div class="span6">
                <ul id="timeline">
''' % {'user': user}

tweets_file.write(html_head)

for x in range(100000):
    url_with_page_num = url + str(x)
    print 'Scanning page %d (%s)' % (x, url_with_page_num)

    f = urlopen(url_with_page_num)
    soup = BeautifulSoup(f.read())
    f.close()

    tweets = soup.findAll('span', {'class': 'status-body'})

    if len(tweets) == 0:
        break

    [tweets_file.write('<li>%s</li>' % tweets[i].renderContents()) for i in range(len(tweets))]

    time.sleep(3)  # being nice to twitter's servers

print 'Scan complete!!'

html_footer = '''
                </ul> <!-- end timeline -->
            </div> <!-- end span6 -->
        </div> <!-- end row -->
    </div> <!-- end container -->


<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js"></script>
<script src="http://twitter.github.com/bootstrap/assets/js/bootstrap-collapse.js"></script>
<script>
$(document).ready(function(){
    $('a[rel~=nofollow], .tweet-url, .entry-meta a').attr('target', '_blank');

    // Souping Twitter returns relative paths,
    // so let's make those into abs paths...
    $('.hashtag, .username').each(function(k, v){
        var $v = $(v);
        $(v).attr('href', 'http://twitter.com'+$(v).attr('href'));
    });
});
</script>

</body>
</html>
'''

tweets_file.write(html_footer)
tweets_file.close()
