import xmlrpclib
import random


class Magento(object):
    URL = 'https://www.yoursitehere.com/index.php/api/xmlrpc'
    usr = 'usernamehere'
    passwd = 'password'
    svr = ''
    token = ''

    def __init__(self, URL=None, usr=None, passwd=None):
        if URL <> None:
            self.URL = URL
        if usr <> None:
            self.usr = usr
        if passwd <> None:
            self.passwd = passwd
        random.seed()

    def connect(self, URL=None, usr=None, passwd=None):
        if URL == None:
            URL = self.URL
        if usr == None:
            usr = self.usr
        if passwd == None:
            passwd = self.passwd
        self.svr = xmlrpclib.ServerProxy(URL)
        self.token = self.svr.login(usr, passwd)

    def getProductArray(self,enabled=True):
        filter = []
        if enabled:
            filter = [{'status': '1'}]
        return self.svr.call(self.token, 'catalog_product.list', filter)

    def getProductInfo(self, products):
        return self.svr.call(self.token, 'catalog_product.info', [products])

    def updateProductInfo(self, data):
        return self.svr.call(self.token, 'catalog_product.update', data)


if __name__ == "__main__":

    Mage = Magento()
    Mage.connect()

    products = Mage.getProductArray()
    for p in products:
        try:
            print '----' * 10
            pid = p['product_id']
            sku = p['sku']

            info = Mage.getProductDescription(p.get('product_id'))

            meta_title = info['meta_title']
            meta_description = info['meta_description']
            name = info['name']

            print meta_title, meta_description

            new_meta_title = '%s | %s' % (name, '<SITE NAME HERE>')
            new_meta_description = 'Shop %s at <SITE NAME HERE>' % (name)

            data = [
                sku, {'meta_title': new_meta_title, 'meta_description': new_meta_description}]
            Mage.updateProductInfo(data)
            print data
        except:
            ## TODO: Handle exceptions
            print sku, 'is broken!!!!!!!!!!!!!'
            pass