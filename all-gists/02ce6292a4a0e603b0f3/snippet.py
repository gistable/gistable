#-*- encoding: utf-8 -*-
import random


def open_door(doors, answer, choice):
    rest_doors = [x for x in doors if x is not choice]
    opened_door = random.choice([x for x in rest_doors if x is not answer])
    return [x for x in doors if x is not opened_door]

doors = [1, 2, 3]

trials = 100000
count1 = 0  # 変更しない場合
count2 = 0  # 変更した場合
for i in range(trials):
    answer = random.choice(doors)
    choice = random.choice(doors)
    new_doors = open_door(doors, answer, choice)

    if answer is choice:
        count1 += 1

    new_choice = random.choice([x for x in new_doors if x is not choice])
    if answer is new_choice:
        count2 += 1

print u"試行回数", trials, u"回"
print u"変更しない場合の正解確率", 100.0 * count1 / trials, "%"
print u"変更した　場合の正解確率", 100.0 * count2 / trials, "%"
