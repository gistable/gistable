#coding: UTF-8

'''
Created on 2014/11/08

@author: shirasu
'''

import random

if __name__ == '__main__':
    realstr = "おっぱいそんちくびんびん"
    strtuple = ("おっ", "ぱい", "そん", "ちく", "びん", "びん")
    count = 0
    while True:
        count += 1
        numlist = []
        
        i = 0
        while i < 6:
            num = random.randint(0,5)
            if num in numlist:
                continue
            numlist.append(num)
            i += 1
            
        string = ""
        for num in numlist:
            string += strtuple[num]
            
        print str(count) + " " + string
        
        if string == realstr:
            print "おめでとうございます！",
            print "あなたは" + str(count) + "回目に" + realstr + "しました。"
            break
        
    print "end"