# -*- coding: utf8 -*-

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from google.appengine.ext import db

class TestModel(db.Model):
    message = db.StringProperty()

class TransactionTest():
    def run_transaction_test(self):
        try:
            db.run_in_transaction(self.transaction)
            return True
        except:
            return False

# 成功
class Test0(TransactionTest):
    def transaction(self):
        a = TestModel(key_name='reni0', message=u'がんばれに')
        a.put()

# 失敗
class Test1(TransactionTest):
    def transaction(self):
        a = TestModel(key_name='shiorin1', message=u'しおりんうれしおりん')
        a.put()
        b = TestModel(key_name='kanako1', message=u'かなこぉ↑')
        b.put()

# 失敗
class Test2(TransactionTest):
    def __init__(self):
        a = TestModel(key_name='shiorin2', message=u'しおりんうれしおりん')
        a.put()
    def transaction(self):
        a = TestModel.get_by_key_name('shiorin2')
        b = TestModel(key_name='odagirishiorin2', message=a.message)
        b.put()

# 失敗
class Test3(TransactionTest):
    def __init__(self):
        a = TestModel(key_name='kanako3', message=u'かなこぉ↑')
        a.put()
    def transaction(self):
        a = TestModel.get_by_key_name('kanako3')
        a.delete()
        b = TestModel(key_name=u'momoka3', message=u'有安でありやす')
        b.put()

# 成功
class Test4(TransactionTest):
    def transaction(self):
        a = TestModel(key_name='shiorin4', message=u'しおりんショック＞＜')
        a.put()
        b = TestModel(key_name='odagirishiorin4', message=u'お゛た゛き゛り゛し゛お゛り゛です', parent=a)
        b.put()

# 成功
class Test5(TransactionTest):
    def transaction(self):
        a = TestModel(key_name='shiorin5', message=u'滅相もない')
        a.put()
        b = TestModel(key_name='odagirishiorin5', message=u'お゛た゛き゛り゛し゛お゛り゛です', parent=a)
        b.put()
        c = TestModel(key_name='uran5', message=u'う゛ら゛ん゛です', parent=a)
        c.put()

# 成功
class Test6(TransactionTest):
    def __init__(self):
        a = TestModel(key_name='shiorin6', message=u'さびしおりん')
        a.put()
        b = TestModel(key_name='odagirishiorin6', message=u'お゛た゛き゛り゛し゛お゛り゛です', parent=a)
        b.put()
        c = TestModel(key_name='uran6', message=u'う゛ら゛ん゛です', parent=a)
        c.put()
    def transaction(self):
        a = TestModel.get_by_key_name('shiorin6')
        b = TestModel.get_by_key_name('odagirishiorin6', a)
        b.message = u'に゛ゃー'
        b.put()
        c = TestModel.get_by_key_name('uran6', a)
        c.message = u'わ゛ぁー'
        c.put()

# 成功
class Test7(TransactionTest):
    def __init__(self):
        a = TestModel(key_name='shiorin7', message=u'しおりんショック＞＜')
        a.put()
        b = TestModel(key_name='odagirishiorin7', message=u'お゛た゛き゛り゛し゛お゛り゛です', parent=a)
        b.put()
        c = TestModel(key_name='uran7', message=u'う゛ら゛ん゛です', parent=a)
        c.put()
        a.delete()
    def transaction(self):
        parent_key = db.Key.from_path('TestModel', 'shiorin7')
        b = TestModel.get_by_key_name('odagirishiorin7', parent_key)
        b.message = u'に゛ゃー'
        b.put()
        c = TestModel.get_by_key_name('uran7', parent_key)
        c.message = u'わ゛ぁー'
        c.put()

# 成功
class Test8(TransactionTest):
    def transaction(self):
        a = TestModel(key_name='shiorin8', message=u'しおりんショック＞＜')
        a.put()
        b = TestModel(key_name='odagirishiorin8', message=u'お゛た゛き゛り゛し゛お゛り゛です', parent=a)
        b.put()
        c = TestModel(key_name='ruka8', message=u'るかです', parent=b)
        c.put()

# 成功
class Test9(TransactionTest):
    def __init__(self):
        a = TestModel(key_name='shiorin9', message=u'しおりんショック＞＜')
        a.put()
        b = TestModel(key_name='odagirishiorin9', message=u'お゛た゛き゛り゛し゛お゛り゛です', parent=a)
        b.put()
        c = TestModel(key_name='ruka9', message=u'るかです', parent=b)
        c.put()
        b.delete()
    def transaction(self):
        a = TestModel.get_by_key_name('shiorin9')
        a.message = u'悲しおりん'
        a.put()
        b = db.Key.from_path('TestModel', 'shiorin9', 'TestModel', 'odagirishiorin9')
        c = TestModel.get_by_key_name('ruka9', b)
        c.message = u'悲しおりん'
        c.put()

class TransactionDispatcher(webapp.RequestHandler):
    def get(self, num=''):
        n = int(num)
        transaction_class_list = [
            Test0, Test1, Test2, Test3, Test4,
            Test5, Test6, Test7, Test8, Test9
        ]
        
        if n >= len(transaction_class_list):
            self.redirect('/transaction/index')
        
        t = transaction_class_list[n]()
        if t.run_transaction_test():
            self.response.out.write('<html><body>Test%s is success.</body></html>' % num)
        else:
            self.response.out.write('<html><body>Test%s is error.</body></html>' % num)

class MainHandler(webapp.RequestHandler):
    def get(self):
        w = self.response.out.write
        w('<html><body>')
        for i in range(10):
            w('<p><a href="/transaction/test%s">Test%s</a></p>' %
                (str(i), str(i)))
        w('</body></html>')

application = webapp.WSGIApplication(
    [('/transaction/test([\d]+)', TransactionDispatcher),
     ('/transaction/index', MainHandler)],
    debug=True)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()
