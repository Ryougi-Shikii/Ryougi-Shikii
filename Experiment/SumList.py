a=[1,3,5,4,2]
# -> len(list) -> O(1) :D

def SumList(arr,size=len(a)): 
    if size<=0:
        return 0
    return arr[size-1]+SumList(arr,size-1)
print(SumList(a))

def SumList2(arr,ind=0):
    if ind==len(arr):
        return 0
    return arr[ind] + SumList2(arr,ind+1)
print(SumList2(a))