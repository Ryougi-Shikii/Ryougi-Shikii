# x^y
def power(x:int,y:int):
    if y==1:
        return x
    return x*power(x,y-1)
print(power(2,5))

# optimal -> O(log(n))
# 2**5 -> inbuilt fuction of python, Find its time complexity

def power2(x, y):
    if y == 0:
        return 1
    if y % 2 == 0:
        half = power2(x, y // 2)
        return half * half
    else:
        return x * power2(x, y - 1)
print(power2(2,5))