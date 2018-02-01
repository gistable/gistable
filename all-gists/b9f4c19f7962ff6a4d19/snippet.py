>>> import robotparser
>>> rp = robotparser.RobotFileParser('http://archivists.metapress.com/robots.txt')
>>> rp.read()
>>> rp.can_fetch('Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)', '/content/953m4u0116t20624/?p=bf20338aa6ef4bc0a60dac3f2c38a6bd&pi=2')
False