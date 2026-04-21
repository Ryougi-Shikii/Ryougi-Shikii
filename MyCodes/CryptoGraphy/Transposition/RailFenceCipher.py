
def RailFence(text, fence):
    rails = []
    for _ in range(fence):
        rails.append([])
    i = 0
    order = False
    for c in text:
        if i == 3:
            order = not order
        if i == 0:
            order = not order
        rails[i].append(c)
        if order:
            i+=1
        else:
            i-=1
    res = ''
    for rail in rails:
        res += ''.join(rail)
    return res

fence = 4
word = 'InformationSecurity'
print(RailFence(word, fence))
