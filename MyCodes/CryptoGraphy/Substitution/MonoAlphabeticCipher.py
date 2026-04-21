import string
SubstituteList = [ c for c in 'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM' ]
SubstitutionTable = { letter : substitute for letter, substitute in zip(string.ascii_letters, SubstituteList)  }

def MonoAlphabetic(word):
    result = ''
    for c in word:
        if c.isalpha():
            result += SubstitutionTable[c]
        else:
            result += c
    return result

word = 'sumit'
print(MonoAlphabetic(word))
