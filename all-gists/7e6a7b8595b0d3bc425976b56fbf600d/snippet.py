print'CALCULATOR'
def addition(a,b):
    return a+b
def substraction(a,b):
    return a-b
def multiplication(a,b):
    return a*b
def division(a,b):
    return a/b
print('select operation.')
print('1.addition')
print('2.substraction')
print('3.multiplication')
print('4.division')
x=int(raw_input('enter no 1:'))
y=int(raw_input('enter no 2:'))

choice=input('choice(1,2,3,4):')
if choice==1:
    s=addition(x,y)
    print'%d+%d=%d'%(x,y,s)
elif choice==2:
    t=substraction(x,y)
    print'%d-%d=%d'%(x,y,t)
elif choice==3:
    u=multiplication(x,y)
    print'%d*%d=%d'%(x,y,u)
elif choice==4:
    v=division(x,y)
    print'%d/%d=%d'%(x,y,v)
else:
    print'invalid'
