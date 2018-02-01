def wintestif(x,y,table) :
    if table[x][y] == 1 :
        return "x"
    elif table[x][y] == 2 :
        return "o"
    else :
        return False
def wintest(table) :
    if table[0][0] == table[1][0] and table[1][0] == table[2][0] :
        return wintestif(0,0,table)
    elif table[0][1] == table[1][1] and table[1][1] == table[2][1] :
        return wintestif(0,1,table)
    elif table[0][2] == table[1][2] and table[1][2] == table[2][2] :
        return wintestif(0,2,table)
    elif table[0][0] == table[0][1] and table[0][1] == table[0][2] :
        return wintestif(0,0,table)
    elif table[1][0] == table[1][1] and table[1][1] == table[1][2] :
        return wintestif(1,0,table)
    elif table[2][0] == table[2][1] and table[2][1] == table[2][2] :
        return wintestif(2,0,table)
    elif table[0][0] == table[1][1] and table[1][1] == table[2][2] :
        return wintestif(0,0,table)
    elif table[0][2] == table[1][1] and table[1][1] == table[2][0] :
        return wintestif(0,2,table)
    else:
        return False
def get_Co(help_text):
    return int(input(help_text))
def ggtv(game):
    if game[0][0] == 0:
        ggtv.a1 = " "
    elif game[0][0] == 1:
        ggtv.a1 = "X"
    elif game[0][0] == 2:
        ggtv.a1 = "O"
    if game[1][0] == 0:
        ggtv.a2 = " "
    elif game[1][0] == 1:
        ggtv.a2 = "X"
    elif game[1][0] == 2:
        ggtv.a2 = "O"
    if game[2][0] == 0:
        ggtv.a3 = " "
    elif game[2][0] == 1:
        ggtv.a3 = "X"
    elif game[2][0] == 2:
        ggtv.a3 = "O"
    if game[0][1] == 0:
        ggtv.b1 = " "
    elif game[0][1] == 1:
        ggtv.b1 = "X"
    elif game[0][1] == 2:
        ggtv.b1 = "O"
    if game[1][1] == 0:
        ggtv.b2 = " "
    elif game[1][1] == 1:
        ggtv.b2 = "X"
    elif game[1][1] == 2:
        ggtv.b2 = "O"
    if game[2][1] == 0:
        ggtv.b3 = " "
    elif game[2][1] == 1:
        ggtv.b3 = "X"
    elif game[2][1] == 2:
        ggtv.b3 = "O"
    if game[0][2] == 0:
        ggtv.c1 = " "
    elif game[0][2] == 1:
        ggtv.c1 = "X"
    elif game[0][2] == 2:
        ggtv.c1 = "O"
    if game[1][2] == 0:
        ggtv.c2 = " "
    elif game[1][2] == 1:
        ggtv.c2 = "X"
    elif game[1][2] == 2:
        ggtv.c2 = "O"
    if game[2][2] == 0:
        ggtv.c3 = " "
    elif game[2][2] == 1:
        ggtv.c3 = "X"
    elif game[2][2] == 2:
        ggtv.c3 = "O"
def gametable():
    return topple + "| %s | %s | %s |\n"% (ggtv.a1,ggtv.b1,ggtv.c1)+topple+"| %s | %s | %s |\n"% (ggtv.a2,ggtv.b2,ggtv.c2)+topple+"| %s | %s | %s |\n"% (ggtv.a3,ggtv.b3,ggtv.c3)+topple


game = [[0, 0, 0],
        [0, 0, 0],
        [0, 0, 0]]

topple = " ---"*3 + "\n"


rnd = 1
ggtv(game)
print(gametable())
while rnd < 10 :
    if wintest(game) == False :
        if rnd % 2 != 0 :
            print(">Round = %d , X plays " % rnd)
            xx= get_Co(">Enter the coordinates:\n>X=")
            yx= get_Co(">Y=")
            if game[yx-1][xx-1] == 0:
                game[yx-1][xx-1] = 1
                rnd +=1
                ggtv(game)
                print(gametable())
            else :
                print("=>That block is already filled.")
                ggtv(game)
                print(gametable())
        else :
            print(">Round = %d , O plays " % rnd)
            xo=get_Co(">Enter the coordinates:\n>X=")
            yo=get_Co(">Y=")
            if game[yo-1][xo-1] == 0 :
                game[yo-1][xo-1] = 2
                rnd +=1
                ggtv(game)
                print(gametable())
            else:
                print("=>That block is already filled.")
                ggtv(game)
                print(gametable())
    else:
        winner = wintest(game)
        print("THE GAME IS OVER\n=>%s won in round %d" % (winner , rnd-1))
        break
if rnd == 10 :
    if wintest(game) == False :
        print("DRAW !")
    else:
        print("%s WON" % winner)