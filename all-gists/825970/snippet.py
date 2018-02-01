#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @author:      starenka
# @email:       'moc]tod[liamg].T.E[0aknerats'[::-1]
# @version:     1.0
# @since        2/14/11
# @depends      DJC

import random, time, sys, datetime
from scenes import Zalozna,Venku
from animals import Dog
from persons import *
from sprites import *

Zalozna.spawn(SlecnaTicha())
while SlecnaTicha.count_notes():
    if random.randint(1, 10) == 8:
        DrobnyMuzikSTaskou = Man(name='Maralík',
                                size='XS',
                                disguise=True,
                                sneak=True,
                                inventory={'taška':[]}
                                )
        Zalozna.spawn(DrobnyMuzikSTaskou)
        break

DrobnyMuzikSTaskou.say(SlecnaTicha,'Ruce vzhůru, sice střelím !')
DrobnyMuzikSTaskou.inventory['taška'].append('celý lup')
DrobnyMuzikSTaskou.disappear()
Venku.spawn(DrobnyMuzikSTaskou)
del(Zalozna.DrobnyMuzikSTaskou)

time.sleep(0)
Zalozna.spawn(Trachta(experience=float('infinity')))
repr(Trachta)
Trachta.say(SlecnaTicha,
            'Žádné strachy, slečno Tichá.'.join(['','Však my si ho najdeme','My mu tipec zatneme.']))
SlecnaTicha.worry(False)

for b in [0,random.choice((2,3))]: Trachta.whistle.blow()
Doubrava = Dog(sex='fenka',name='Doubrava')
Zalozna.spawn(Doubrava)
Doubrava.sniff().sniff()
repr(Doubrava)

for i in [Trachta,Doubrava,SlecnaTicha]:
    Venku.spawn(i)
    del(Zalozna.i)

Venku.spawn([Blato(),Strom()])
Trachta.say(Doubrava,'Čile za ním!')
Doubrava.ignore().procrastinate()

chlapci = []
for m in range(0,6):
    chlapec = Man(name='Chlapec #%d'%m)
    chlapci.append(chlapec)
    Venku.spawn(chlapec)

Trachta.say(chlapci,'Sekeru a pilu, chlapci. Nestůjte tu nečinně.')
time.sleep(.5)
Trachta.say(chlapci,'Lupič zřejmě přichystal si úkryt v stromu dutině.')

while chlapci.cut(Strom,chainsaw=False):
    if random.randint(1, 10) == 4:
        DrobnyMuzikSTaskou.say(Trachta,
                               'Dostal jste mě inspektore ! Sedím přímo nad vámi !',
                               shout=True,dramatic=True,fear=.8)
        break

Venku.rotate()
if Strom.branches[-1].get_content() == DrobnyMuzikSTaskou:
    Trachta.say(DrobnyMuzikSTaskou,'odpykáš')
    Trachta.arrest(DrobnyMuzikSTaskou,inform_rights=False)
    Trachta.praise(Doubrava)
    SlecnaTicha.bpm(72)
    Doubrava.jump(.6)
    DrobnyMuzikSTaskou.disappear(datetime.timedelta(years=4))
    print sys.modules[__name__]


'''
Slečna Tichá za přepážkou bankovky si počítá.
Náhle drobný mužík s taškou v záložně se ocitá.

Nenápadný v overalu, v očích ale rysí svit.
Krokem šelmy měří halu, může to jen lupič být.

"Ruce vzhůru, sice střelím !" Jde to jako na drátkách.
Již má v tašce lup svůj celý a již mizí ve vrátkách.

"Hleďme Trachtu, detektiva !" Na místě je coby dup.
Moudrou hlavou moudře kývá. Je to starý, ostřílený, policejní sup !

"Žádné strachy, slečno tichá. Však my si ho najdeme.
Žádné strachy, slečno tichá. My mu tipec zatneme."

Dva, tři hvizdy na píšťalku, je zde fenka Doubrava.
Podívejme na čmuchalku. Pach stopy již nasává.

Dopadla už jinčí ptáčky. Vlastní řadu diplomů.
Však co to: Hned u zatáčky čichá fena ke stromu.

"Čile za ním", velí Trachta. Ale zvíře nevnímá.
Kolem stromu v blátě čvachtá, povelů si nevšímá.

"Sekeru a pilu, chlapci. Nestůjte tu nečinně.
Lupič zřejmě přichystal si úkryt v stromu dutině."

Řežou dubu tělo sporé. Náhle slyšet volání:
"Dostal jste mě inspektore ! Sedím přímo nad vámi !"

Na větvi byl, lišák jeden ! Nu ten si to odpyká.
Důmyslem a psem svým veden již ho Trachta zatýká.

Slečna Tichá štěstím vzkvétá, veselo skáče chytrý psík.
Lupič dostal čtyři léta. Jmenoval se Maralík.
'''