import feedparser

f=open('blogroll.html','w')
f.write("<html>\n<head>\n<title>Blogroll</title>\n</head>\n<body>");
blogs=["http://programminggenin.blogspot.com/feeds/posts/default","http://djangolearner.blogspot.com/feeds/posts/default"];
for blog in blogs :
	feed=feedparser.parse(blog)
	f.write('<a href="%s">%s</a>\n'% (feed.feed.link,feed.feed.title));
	f.write('<ul>\n');
	for e in feed.entries:
		f.write( '  <li><a href="%s">%s</a></li>\n'% (e.link,e.title) )
	f.write('</ul>\n');
f.write('</body>\n</html>');
