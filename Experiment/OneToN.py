num=10
# num to 1
def f1(n):
    if n==0:
        return
    print(n)
    f1(n-1)
f1(num)

# 1 to num
def f2(n):
    if n==0:
        return
    f2(n-1)
    print(n)
f2(num)

# start from l (=1 default) to num
def f3(n,l=1):
    if l==n+1:
        return
    print(l)
    f3(n,l+1)
f3(num)

# -> tuples has a way to solve expression from left to right
# -> we are using tuples to run instructions but never using tuples!!

f1 = lambda n: None if n == 0 else (print(n), f1(n-1))
f1(10)

f2 = lambda n: None if n == 0 else (f2(n-1), print(n))
f2(10)

f3 = lambda n, l=1: None if l == n+1 else (print(l), f3(n, l+1))
f3(10)
