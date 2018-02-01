#coding=utf-8

'''
* 去除指定类型文件的bom头
* 版权所有
* @author      t6760915<t6760915@gmail.com>
* @version     $Id: trim_bom.py $
'''

import os
import sys
import codecs

class TrimBom:
    
    basePath = ''
    fileList = []
    trimExtList = ['php', 'css', 'js', 'py', 'pl', 'html', 'htm']

    #去除字符串中的bom部分
    def trim_bom(self, str):
        if not str:
            return ''
        
        if len(str) < 3:
            return ''
        
        if str[:3] == codecs.BOM_UTF8:
            return str[3:]
        
        return str

    #去除某文件的bom头
    def trim_file_bom(self, fileName):
        if not fileName:
            return False
        
        if not os.path.exists(fileName):
            return False

        try:
            fp = open(fileName, 'r')
            html_sourse = fp.read()
            fp.close()
        except:
            return False

        html_result = self.trim_bom(html_sourse)

        if html_result == html_sourse:
            return False

        try:
            fp = open(fileName, 'w')
            fp.write(html_result)
            fp.close()
        except:
            return False

        return True

    #获取指定类型文件名列表
    def getFileListByExt(self, path):
        if not path:
            return False

        path = os.path.normpath(path)

        if not os.path.exists(path):
            return False

        if os.path.isfile(path) and path.split('.')[-1] in self.trimExtList:
            trimFlag = self.trim_file_bom(path)

            if trimFlag:
                print 'process %s success...' % path.replace(self.basePath, '').replace('\\', '/')
            
        elif os.path.isdir(path):
            fileNameList = os.listdir(path)
            for fileName in fileNameList:
                fileName = os.path.normpath('%s/%s' % (path,fileName))
                self.getFileListByExt(fileName)
        
        return False

    #运行函数入口
    def run(self, path):
        self.basePath = os.path.normpath(path)
        self.getFileListByExt(path)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'USEAGE:python %s dirName' % __file__
        sys.exit(0)
    
    tObj = TrimBom()
    tObj.run(sys.argv[1])