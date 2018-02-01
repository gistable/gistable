# Created By: Kyle Boulay
# Created On: Oct 27, 2016
# Created For: ICS3U
# Created To: Play 21 Against A Bot

import ui
import random

user_card_1 = random.randint(1, 10)
user_card_2 = random.randint(1, 10)
user_card_3 = random.randint(1, 10)
cpu_card_1 = random.randint(1, 10)
cpu_card_2 = random.randint(1, 10)
cpu_card_3 = random.randint(1, 10)
points = user_card_1 + user_card_2 + user_card_3
cpu_points = cpu_card_1 + cpu_card_2 + cpu_card_3

#global click1
#click1 = 0
#global click2
#click2 = 0
#global click3
#click3 = 0
#global dealer_click
#dealer_click = 0


#print(str(cpu_card_3))

def card1_touched(sender):
    #global click1
    #click1 = 1
    #if dealer_click == 0:
        #pass
    
    view['card1'].text = str(user_card_1)
    view['points'].text = 'Your Points: ' + str(user_card_1)
    

def card2_touched(sender):
    #global click2
    #click2 = 1
    #if click1 == 0:
        #pass
    
    view['card2'].text = str(user_card_2)
    view['points'].text = 'Your Points: ' + str(user_card_2 + user_card_1)
    

def card3_touched(sender):
    #global click3
    #click3 = 1
    #if click2 == 0:
        #pass
        
    view['card3'].text = str(user_card_3)
    view['points'].text = 'Your Points: ' + str(user_card_3 + user_card_2 + user_card_1)
    

def dealer_touched(sender):
    #global dealer_click
    #dealer_click = 1
    #if click3 == 0:
        #pass
    view['cpu_card1'].text = str(cpu_card_1)
    view['cpu_card2'].text = str(cpu_card_2)
    view['cpu_card3'].text = str(cpu_card_3)
    view['cpu_points'].text = 'Dealer Points: ' + str(cpu_card_3 + cpu_card_2 + cpu_card_1)
    
    if points > 21 and cpu_points > 21:
        view['winner'].text = 'No one wins!'
    if points > 21 and cpu_points < 22:
        view['winner'].text = 'Dealer wins!'
    if points < 22 and cpu_points > 21:
        view['winner'].text = 'You win!'
    if points == cpu_points:
        view['winner'].text = 'You tied!'
    if cpu_points > points:
        view['winner'].text = 'Dealer Wins!'
    if points > cpu_points:
        view['winner'].text = 'You Win!'
    if cpu_points < 22 and points > 21:
        view['winner'].text = 'Dealer Wins!'
    if cpu_points > 21 and points < 22:
        view['winner'].text = 'You Win!'

view = ui.load_view()
view.present('full_screen')

