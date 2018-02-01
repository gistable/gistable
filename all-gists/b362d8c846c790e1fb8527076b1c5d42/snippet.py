from turtle import Turtle
from random import randint

grass = Turtle()
grass.color('#007b0c')

sky = Turtle()
sky.color('#e5e5ff')
sky.pensize(100)
sky.speed(0)

tuft = Turtle()

cut = Turtle()
cut.speed(0)
    

lake = Turtle()

mountain = Turtle()
mountain.pensize()
mountain.color('#a9a9a9')
mountain.speed(0)

trees = Turtle()
trees.pensize(5)
trees.color('#654321')

cloud = Turtle()

turtles = [grass,sky,mountain,trees,cloud,lake,tuft,cut]

def penup():
    for i in turtles:
        i.penup()
def pendown():
    for i in turtles:
        i.pendown()
def speed():
    for i in turtles:
        i.speed(0)
        i.hideturtle()


hexnum = ["1","2","3","4","5","6","7","8","9","a","b","c","d","e","f"]

penup()
sky.goto(-200,-200)
pendown()

skycol = ['add8e6','b5d8e5','bdd8e4','c5d8e3','cdd8e3','d6d8e2','ded8e1','e6d8e1','eed8e0','f6d8df','ffd9df']

def drawsky():
    print("Drawing sky")
    for i in skycol:
        temp = '#' + i
        sky.color(temp)
        sky.forward(500)
        sky.left(90)
        sky.forward(20)
        sky.left(90)

        sky.color(temp)
        sky.forward(500)
        sky.right(90)
        sky.forward(20)
        sky.right(90)

def drawmountains():
    penup()
    mountain.goto(-300,-100)
    pendown()
    mountain.begin_fill()
    print("\n")
    print("Drawing mountains 1")
    for i in range(10):
        templen = randint(20,200)
        
        tempang = randint(45,80)
        
        mountain.left(tempang)
        mountain.forward(templen)
        mountain.right(2*tempang)
        mountain.forward(templen)
        mountain.setheading(0)
        
    mountain.goto(300,-400)
    mountain.goto(-300,-400)
    mountain.end_fill()

    mountain.color('#d3d3d3')
    penup()
    mountain.goto(-300,-150)
    pendown()
    mountain.begin_fill()

    print("Drawing mountains 2")
    for i in range(10):
        templen = randint(20,200)
        
        tempang = randint(20,30)
        
        mountain.left(tempang)
        mountain.forward(templen)
        mountain.right(2*tempang)
        mountain.forward(templen)
        mountain.setheading(0)
        
    mountain.goto(300,-400)
    mountain.goto(-300,-400)
    mountain.end_fill()


    mountain.color('#6d8383')
    penup()
    mountain.goto(-300,-165)
    pendown()
    mountain.begin_fill()
    print("Drawing mountains 3")
    for i in range(10):
        templen = randint(20,200)
        
        tempang = randint(10,20)
        
        mountain.left(tempang)
        mountain.forward(templen)
        mountain.right(2*tempang)
        mountain.forward(templen)
        mountain.setheading(0)
        
    mountain.goto(300,-400)
    mountain.goto(-300,-400)
    mountain.end_fill()

browns = ['#7a5230','#614126','#49311c','#302013','#181009']
greens = ['#004000','#003300','#002600','#001900','#004c00']


def drawgrass(amount,locx,locy):
    tuft.color('#004000')
    tuft.hideturtle()
    def tuftdraw(size):
        if randint(0,1) == 1:
            size = -size
        tuft.color(greens[randint(0,4)]) 
        penup()
        tuft.goto(locx+size,locy+size)
        pendown()
        tuft.goto(locx+5+size,locy+10+size)
        tuft.goto(locx+size,locy+size)
        tuft.goto(locx-5+size,locy+10+size)
        tuft.goto(locx-1+size,locy-1+size)
        tuft.goto(locx+3+size,locy+6+size)
        tuft.goto(locx+1+size,locy-1+size)
        tuft.goto(locx-2+size,locy+5+size)
    for i in range(amount):
        for i in range(randint(1,4)):
            tuftdraw(i*3)

    

def drawtrees():

    def grassdraw():
        penup()
        grass.goto(randint(-160,-150),randint(-240,-190))
        
        pendown()
        grass.begin_fill()
        for i in range(200):
            grass.color(greens[randint(0,4)])
            grass.goto(randint(-300,-50),randint(-200,-150))
        
        grass.end_fill()

    def greentree():
            temppos = trees.pos()
            trees.color(greens[randint(0,4)])
            trees.pensize(1)

            trees.setheading(90)
            trees.begin_fill()
            trees.forward(40)
            trees.right(160)
            trees.forward(50)
            trees.end_fill()

            trees.setheading(90)
            trees.goto(temppos)
            trees.begin_fill()
            trees.forward(40)
            trees.left(160)
            trees.forward(50)
            trees.end_fill()

            trees.goto(temppos)
            trees.setheading(90) #part 2
            trees.begin_fill()
            trees.forward(50)
            trees.right(160)
            trees.forward(50)
            trees.end_fill()

            trees.setheading(90)
            trees.goto(temppos)
            trees.begin_fill()
            trees.forward(50)
            trees.left(160)
            trees.forward(50)
            trees.end_fill()

            trees.goto(temppos)
            trees.setheading(90) #part 3
            trees.begin_fill()
            trees.forward(60)
            trees.right(160)
            trees.forward(50)
            trees.end_fill()

            trees.setheading(90)
            trees.goto(temppos)
            trees.begin_fill()
            trees.forward(60)
            trees.left(160)
            trees.forward(50)
            trees.end_fill()

    grassdraw()
    
    print("\n")
    trees.speed(0)

    def treees(treeheight):
        trees.color(browns[randint(0,4)])
        trees.pensize(randint(2,4))
        penup()
            
        trees.goto(treeheight) #goes to random location and draws random length
        pendown()
        trees.setheading(90)
        trees.forward(randint(20,30))

        greentree()
            
        trees.left(270) #turns back to the normal direction


    for i in range(10):
        print("Drawing tree",i+1,"/20")
        temph = randint(-270,-80),randint(-180,-170)
        treees(temph)
    for i in range(10):
        print("Drawing tree",i+11,"/20")
        temph = randint(-270,-80),randint(-200,-190)
        treees(temph)


def clouddraw():
    print("\n")
    cloud.color('white')
    
    def randloc():
        location = randint(-250,250),randint(0,270)
        return location
    
    def brushstroke(randloc,leng):
        penup()
        cloud.goto(randloc)
        pendown()
        cloud.pensize(randint(3,5))
        cloud.forward(leng)
        
    def singlecloud():
        temp = randloc()
        temp2 = temp[1]
        temp3 = temp[0]
        leng = 30
            
        for i in range(20):
            temp4 = (temp3, temp2)
            brushstroke(temp4,leng)
            temp2 += 1
            temp3 += randint(-10,10)
            leng += randint(-40,40)

    for i in range(4):
        print("Drawing cloud:",i+1)
            
        singlecloud()



def lakedraw():
    print("\nDrawing lake")
    blues = ['00004c','000066','000099','0000b2','0000cc','0000e5','0000ff']

    penup()
    lake.goto(randint(-50,50),randint(-170,-150))
    temp = Turtle()
    temp.penup()
    temp.hideturtle()
    temp.goto(lake.pos())
    pendown()

    lake.begin_fill()

    lake.pensize(5)
    for i in range(50):
        lake.color("#"+blues[randint(0,6)])
        lake.forward(5)
        lake.right(randint(0,5)/10)
        if randint(0,2) == 2:
            drawgrass(5,lake.pos()[0],lake.pos()[1])
    while lake.heading() > 185:
        lake.color("#"+blues[randint(0,6)])
        lake.forward(2)
        lake.right(randint(-2,8))
    for i in range(50):
        lake.color("#"+blues[randint(0,6)])
        lake.forward(5)
        lake.left(randint(0,2)/10)
    for i in range(100):
        lake.color("#"+blues[randint(0,6)])
        lake.forward(5)
        lake.right(randint(0,8)/10)
        
    lake.color("#"+blues[1])
    lake.goto(temp.pos())
    lake.end_fill()

def lilypads(amount):
    lily = Turtle()
    lily.speed(0)
    for i in range(amount):
        lily.color(greens[randint(0,4)])
        lily.penup()
        lily.goto(randint(0,200),randint(-300,-175))
        lily.pendown()
        for i in range(2,7):
            lily.forward(2)
            lily.pensize(i)
        for i in range(0,7):
            lily.forward(2)
            lily.pensize(7-i)
    


def cutdraw():
    print("\nCutting out")

    cut.penup()

    cut.color('black')
    cut.pensize(40)
    cut.goto(-250,250)
    cut.pendown()
    cut.goto(250,250)
    cut.goto(250,-250)
    cut.goto(-250,-250)
    cut.goto(-250,250)

    penup()
    cut.speed(9)
    cut.color('white')
    cut.pensize(200)
    cut.goto(-345,345)
    cut.pendown()
    cut.goto(345,345)
    cut.goto(345,-345)
    cut.goto(-345,-345)
    cut.goto(-345,345)


speed() #sets all speeds to fastest

drawsky()

clouddraw()

drawmountains()

lakedraw()

lilypads(25)

drawtrees()

cutdraw() #cuts off the edges

print("\nTa Daaa!")
input()
