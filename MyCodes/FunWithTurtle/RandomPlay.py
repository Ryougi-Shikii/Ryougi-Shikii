#random turtle creation creating sexagon go BOOM!!
import turtle
import random
t = turtle.Screen()
t.setup(800,800)
t.title("looping tutle")
t.bgcolor("black")
side=6
loop=1
def creat(num):
    colours=['red', 'yellow', 'green', 'blue', 'white', 'orange', 'pink'] 
    for k in range(num):
        i=turtle.Turtle()
        i.speed(0)
        i.shape("triangle")
        i.color(colours[random.randrange(0,7)])
        i.setpos(0,0)
        turtl.append(i)
def draw(turt):
    for _ in range(loop):
        for _ in range(side):
            length=random.randrange(90,130)
            turt.left(length/side)
            turt.forward(length)
            turt.right(360/side)
            turt.right(length/side)
        turt.right(360/loop)
for _ in range(100):
    turtl=[]
    creat(1)
    for j,l in enumerate(turtl):
        draw(l)
        side+=1
    if side%5==0:
        side=5
s=input()
