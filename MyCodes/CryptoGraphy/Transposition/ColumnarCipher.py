import string
key = 'crypto'
word = 'InformationSecurity'

postoc = { num : c for num,c in zip([i for i in range(1,53)], string.ascii_letters) }
ctopos = { c : num for num,c in zip([i for i in range(1,53)], string.ascii_letters) }
def Columnar(text, key):
    dic = {c:[] for c in key}
    order = {  }
    for c,letter in zip(key*20, text):
        dic[c].append(letter)
    loop = [ ctopos[i] for i in key ]
    res = ''
    for i in sorted(loop):
        res += ''.join(dic[postoc[i]])
    return res

print(Columnar(word, key))
