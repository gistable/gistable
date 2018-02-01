'''
開始試著把  Python 中，
有名的 tkinter.py 中文化。

tkinter_tc.py

tk_中文化.py
呂仁園， 2014/07/17

'''
from tkinter import *

class 窗類(Tk):
    
    def __init__(我,*x,**y):

        Tk.__init__(我,*x,**y)
        
    def 標題(我,*x,**y):
        '''
        標題： 給窗一個名。
        '''

        我.title(*x,**y)
    
    def 主迴圈(我,*x,**y):
        '''
        主迴圈：讓窗進入主迴圈。
        '''
        我.mainloop(*x,**y)
    pass

class 布類(Canvas):
    
    def __init__(我,*x,**y):
        try:
            y['background']= y.pop('背景色')
        except:
            pass

        Canvas.__init__(我,*x,**y)
    '''
    打包= pack

    造弧= create_arc
    造圖= create_bitmap
    造像= create_image
    造線= create_line
    造圓= create_oval
    造多邊= create_polygon
    造方= create_rectangle
    造字= create_text
    造窗= create_window
    '''
    
    def 造線(我,*x,**y):
        我.create_line(*x,**y)

    def 打包(我,*x,**y):
        我.pack(*x,**y)

    def 造弧(我,*x,**y):
        我.create_arc(*x,**y)

    def 造圖(我,*x,**y):
        我.create_bitmap(*x,**y)

    def 造像(我,*x,**y):
        我.create_image(*x,**y)

    def 造線(我,*x,**y):
        我.create_line(*x,**y)

    def 造圓(我,*x,**y):
        我.create_oval(*x,**y)

    def 造多邊(我,*x,**y):
        我.create_polygon(*x,**y)

    def 造方(我,*x,**y):
        我.create_rectangle(*x,**y)

    def 造字(我,*x,**y):
    
        try:
            y['text']= y.pop('字')
        except:
            pass

        我.create_text(*x,**y)

    def 造窗(我,*x,**y):
        我.create_window(*x,**y)

def 主程式():

    窗= 窗類()
    窗.標題('窗')

    布= 布類(窗, 背景色= 'yellow')
    布.打包()

    布.造方(100,100,200,200)
    布.造圓(100,100,200,200)
    布.造多邊(100,150,150,100,200,200)

    布.造線(100,20,200,20)
    布.造字(150,30, 字= '造線、字、方、圓、多邊。')
    布.造線(100,40,200,40)

    布.造字(100, 90, 字= '方左上座標= (100,100)')
    

    窗.主迴圈()

if __name__=='__main__':

    主程式()

