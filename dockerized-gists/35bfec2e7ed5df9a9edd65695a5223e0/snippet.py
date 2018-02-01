#-*_coding:utf8-*-
from multiprocessing.dummy import Pool as ThreadPool
import re,requests
import urllib2
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
class spider(object):
    def get_source(self,url):
        hds={
        'Connection': 'Keep-Alive',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
        'User-Agent': 'Googlebot/2.1 (+http://www.googlebot.com/bot.html)',
        'Host': 'www.tianyancha.com',
        'Referer': 'http://antirobot.tianyancha.com/captcha/verify?return_url=http://www.tianyancha.com/search/%E6%B1%9F%E8%A5%BF%20%20%20%E4%BA%BA%E5%8A%9B%E8%B5%84%E6%BA%90/11'
}
        req = urllib2.Request(url, data=None, headers=hds)
        response = urllib2.urlopen(req)
        return response.read()
    def get_companyurl(self,source):
        companyurl=re.findall('<a href="(.*)" ng-click',source)
        companyurl_group=[]
        for j in companyurl:
            every_companyurl='http://www.tianyancha.com' + j
            companyurl_group.append(every_companyurl)
        return companyurl_group
    def get_companyinfo(self,source):
        try:
                info={}
                company_baseinfo=re.findall('class="ng-binding">(.*?)</p>',source)
            # while company_baseinfo: #不知道为何无法实现换业 我的心在滴血。。。
                print company_baseinfo[0]
                info['company_name']=company_baseinfo[0]
                print '公司名称：'+company_baseinfo[1]
                info['Registered_Capital']=company_baseinfo[1].replace('&nbsp;','')
                print '注册资本：'+info['Registered_Capital']
                info['register_date']=company_baseinfo[2]
                print '注册时间：'+info['register_date']
                info['shareholder_info']=re.search('<meta name="description" content="(.*?)"',source,re.S).group(1)
                print '股东信息：'+info['shareholder_info']
                info['scope_of_business']=re.search('经营范围：</span>([\s\S]*)</p><!-- end ngIf: company.baseInfo.businessScope -->',source).group(1)
                print '经营范围：'+info['scope_of_business']
                info['register_place']=re.search('注册地址：</span>([\s\S]*)</p><!-- end ngIf: company.baseInfo.regLocation -->',source,re.S).group(1)
                print '注册地址：'+info['register_place']
                # info['conection_info']=re.search('<span class="contact_way_title">邮箱:</span>([\s\S]*)@qq.com',source,re.S).group(1) 如果抓取为空就会影响整个程序运行。。。
                # print '联系方式'+info['conection_info']
                return info
        except IndexError:
            print('No organization match for {}')

    def saveinfo(self,companyinfo):
        f=open('jiangxiHr.txt','a')
        for each in companyinfo:
            f.writelines('公司名称:'+each['company_name']+'\n')
            f.writelines('注册资本:'+each['Registered_Capital']+'\n')
            f.writelines('注册时间:'+each['register_date']+'\n')
            f.writelines('股东信息:'+each['shareholder_info']+'\n')
            f.writelines('经营范围:'+each['scope_of_business']+'\n')
            f.writelines('注册地址:'+each['register_place']+'\n')
        f.close()
if __name__ == '__main__':
    pool = ThreadPool(4)
    classinfo = []
    HRspider = spider()
    for i in range(1,15):
        url='http://www.tianyancha.com/search/%E6%B1%9F%E8%A5%BF%20%20%20%E4%BA%BA%E5%8A%9B%E8%B5%84%E6%BA%90/'+ str(i)
        print u'正在处理页面：' + url
        html=HRspider.get_source(url)
        get_companylink=HRspider.get_companyurl(html)
        for eachlink in get_companylink[1:19]:
            companysource=HRspider.get_source(eachlink)
            companyinfo=HRspider.get_companyinfo(companysource)
            classinfo.append(companyinfo)
    HRspider.saveinfo(classinfo)
    pool.close()
    pool.join()

