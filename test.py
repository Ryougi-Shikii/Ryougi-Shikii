import random
MIN_SEARCH_DELAY = 13
MAX_SEARCh_DELAY = 17
arr = []
for _ in range(3000):
    delay = round(random.uniform(MIN_SEARCH_DELAY, MAX_SEARCh_DELAY), 1)
    arr.append(delay)
print(arr)
print(sum(arr)/len(arr))