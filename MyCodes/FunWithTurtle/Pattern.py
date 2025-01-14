import turtle
t = turtle.Screen()
t.setup(800,800)
t.title("looping tutle")
t.bgcolor("black")
side=8
loop=8
def creat(num):
    for k in range(num):
        i=turtle.Turtle()
        i.speed(0)
        i.shape("triangle")
        i.color("pink")
        i.setpos(0,0)
        turtleList.append(i)
def draw(turt,leng):
    for _ in range(loop):
        for _ in range(side):
            turt.forward(leng)
            turt.right(360/side)
        turt.right(360/loop)
turtleList=[]
creat(1)
for j,l in enumerate(turtleList):
    draw(l,100)
for _ in range(3):
    side+=2
    loop+=1
    draw(turtleList[0],100)

        
s=input()
