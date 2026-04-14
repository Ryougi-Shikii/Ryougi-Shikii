import matplotlib.pyplot as plt

x=[x for x in range(11)]
y=[y for y in range(11)]
#plt.plot(x,y, 'ro')
plt.plot(x,y,label="squaring: x=x**2",color="red")
plt.axis([0, 6, 0, 20])

plt.show()

