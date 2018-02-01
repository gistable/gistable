import math
import os
import sys
def cls():
    os.system(['clear','cls'][os.name == 'nt'])


def quadratic():
    a = int(input('enter a: '))
    b = int(input('enter b: '))
    c = int(input('enter c: '))
    D = b**2-4*a*c
    if D < 0:
        print 'no solution'
    elif D == 0:
        print round((-b)/(2*a),2)
    else:
        print 'x1=' , round((-b+math.sqrt(D))/(2*a),2)
        print 'x2=' , round(-b-math.sqrt(D))/(2*a)
    menu()

def menu():
    
    print 'choose:\n start again - 1 \n quit - 2 '
    choice = int(input('choose'))
    if choice == 1:
        cls()
        quadratic()
    elif choice ==2:
        sys.exit


quadratic()