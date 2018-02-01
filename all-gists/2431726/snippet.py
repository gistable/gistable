"""
Код, который можно использовать, чтоб понять, какого рода 
насоздавались питоновые объекты за время между вызовами 
с creageGcIds() и newGcIdsAndBreak(). Вторая функция, 
очевидно, выкинет сразу в отладчик.

Можно использовать, когда на интересующие объекты 
не получается поставить weakref. (с) Леонид Евдокимов.

См. также http://homo-virtualis.livejournal.com/25634.html
Exception #08: Поиск утечек памяти в python-программе.
"""

import gc
import pdb

gcIds = set()

def createGcIds():
    global gcIds
    gcIds.update(map(id, gc.get_objects()))

def newGcIdsAndBreak():
    newObjs = []
    for obj in gc.get_objects():
        if id(obj) not in gcIds:
            newObjs.append(obj)
            print obj
    pdb.set_trace()
    newObjs.clear()