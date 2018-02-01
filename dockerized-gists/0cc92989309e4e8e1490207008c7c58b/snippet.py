#martin@muimota.com
#grabs stocks values from Yahoo finance
from lxml import html
import urllib2

#curl -vs https://es.finance.yahoo.com/q?s=ITX.MC 2>/dev/null | xmllint --html --xpath '//*[@id="yfs_l84_itx.mc"]' - 2>/dev/null

def query(symbol):

    url   = 'http://finance.yahoo.com/quote/{}'.format(symbol.upper())
    page  = urllib2.urlopen(url).read()
    tree  = html.fromstring(page)

    price =  tree.xpath('//*[@id="quote-header-info"]/section/span[1]/text()')
    name  =  tree.xpath('//*[@id="quote-header-info"]/div[1]/h6/text()')

    return name+price

def getIBEX35():
    url   = 'https://es.finance.yahoo.com/q/cp?s=%5EIBEX'
    page  = urllib2.urlopen(url).read()
    tree  = html.fromstring(page)
    stocks = []
    for i in range(35):
        #tbody removed http://stackoverflow.com/a/5586627/2205297
        xpath = '//*[@id="yfncsumtab"]/tr[2]/td[1]/table[2]/tr/td/table/tr[{}]'.format(i+2)
        symbol = tree.xpath(xpath+'/td[1]/b/a/text()')[0]
        name   = tree.xpath(xpath+'/td[2]/text()')[0]
        price  = tree.xpath('//*[@id="yfs_l84_{}"]/text()'.format(symbol.lower()))[0]
        price  = float(price.replace(',', '.'))#convert string to float
        stockinfo = (symbol,name,price)
        stocks.append(stockinfo)
    return stocks

if __name__ == '__main__':
    ibex35 = (
        'ABE.MC','ACS.MC','ACX.MC','AENA.MC','AMS.MC','ANA.MC','BBVA.MC',
        'BKIA.MC','BKT.MC','CABK.MC','CLNX.MC','DIA.MC','ELE.MC','ENG.MC',
        'FCC.MC','FER.MC','GAM.MC','GAS.MC','GRF.MC','IAG.MC','IBE.MC',
        'IDR.MC','ITX.MC','MAP.MC','MRL.MC','MTS.MC','POP.MC','REE.MC','REP.MC',
        'SAB.MC','SAN.MC','TEF.MC','TL5.MC','TRE.MC','VIS.MC',
    )
    #get all info in one request
    print getIBEX35()
    #checks every IBEX35's stock
    #for symbol in ibex35:
    #    print query(symbol)
