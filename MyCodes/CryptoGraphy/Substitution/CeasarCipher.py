def caesar(text, shift):
    result = ''
    for c in text:
        if c.isalpha():
            shifted = chr((ord(c.lower()) - ord('a') + shift) % 26 + ord('a'))
            result+=shifted
        else:
            result+=c
    return result

shift = 3
word = "sumit"
print(f"{word} -> ", caesar(word, shift))