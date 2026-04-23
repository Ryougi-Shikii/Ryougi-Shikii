a=[23,5,35,55,6,7]
def MinMax(arr, i=0):
    if i == len(arr) - 1:
        return arr[i], arr[i]
    mini, maxi = MinMax(arr, i + 1)
    return min(arr[i], mini), max(arr[i], maxi)
print(MinMax(a))