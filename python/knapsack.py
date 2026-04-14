
wt=[1,3,4,5]
vt=[1,4,5,7]
w=10
n=4

def knapsack(wt, vvt, w, n):
    
    if (w==0 or n==0):
        return 0
    
    if wt[n-1]>w:
        return knapsack(wt,vvt,w,n-1)
    if wt[n-1]<=w:
        return max(vvt[n-1]+knapsack(wt,vvt,w-wt[n-1],n-1),knapsack(wt,vvt,w,n-1))

print(knapsack(wt,vt,w,n))
