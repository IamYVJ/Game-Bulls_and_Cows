import json

dictionary = {}

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

def get_word():
    word = input('Enter Word: ').upper().strip()
    while len(word)!=4 and word not in dictionary[word[0]]:
        word = input('Enter Word: ').upper().strip()
    return word

def get_guess():
    guess = input('Enter Guess: ').upper().strip()
    while len(guess)!=4 and guess not in dictionary[guess[0]]:
        guess = input('Enter Guess: ').upper().strip()
    return guess

def get_dictionary():
    global dictionary
    with open('words.json') as f:
        dictionary = json.loads(f.read())


def main():
    get_dictionary()
    word = get_word()
    print()
    game_over = False
    while not game_over:
        guess = get_guess()
        bulls, cows = check(word, guess)
        print(f'{bulls} Bulls & {cows} Cows\n')
        if bulls==4:
            game_over=True

if __name__ == "__main__":
    main()