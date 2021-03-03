def check(word, guess):
    word = word.upper().strip()
    guess = guess.upper().strip()
    word = list(word)
    guess = list(guess)
    bulls = 0
    cows = 0
    index = 0
    while index<len(word):
        if word[index]==guess[index]:
            bulls+=1
            del word[index]
            del guess[index]
        else:
            index+=1
    index = 0
    while index<len(word):
        index2 = 0
        found = False
        while index2<len(guess):
            if word[index]==guess[index2]:
                cows+=1
                del word[index]
                del guess[index2]
                found = True
                break
            else:
                index2+=1
        if not found:
            index+=1
    return [bulls, cows]

print(check('hell', 'leol'))