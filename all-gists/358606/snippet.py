import urllib
print 'javascript:' + urllib.quote("""
(function(){
var e = document.createElement('script');
e.src='/boot.js';
e.type='text/javascript';
document.getElementsByTagName('body')[0].appendChild(e);})()
""".strip().replace('\n', ' '))
