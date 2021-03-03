import json
from random import randint, choice
import os, sys

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

def get_random_word():
    alpha = chr(ord('A') + randint(0, 25))
    word = choice(dictionary[alpha])
    return word

def get_guess():
    guess = input('Enter Guess: ').upper().strip()
    if guess=='IQUIT':
        return guess
    while len(guess)!=4 or guess not in dictionary[guess[0]]:
        print('Invalid Guess. Try Again!')
        guess = input('Enter Guess: ').upper().strip()
        if guess=='IQUIT':
            break
    return guess

def get_dictionary():
    dictionary_path = 'words.json'
    if getattr(sys, 'frozen', False):
        dictionary_path = os.path.join(sys._MEIPASS, 'words.json')
    global dictionary
    with open(dictionary_path) as f:
        dictionary = json.loads(f.read())

def print_line():
    print()
    print('-----------------------------------------------------------------------------')
    print()

def print_header():
    print()
    print_line()
    print('\t\t\tBulls and Cows - By YVJ Systems')
    print('\t\t\t\tVersus Computer')
    print_line()

def main():
    print_header()
    get_dictionary()
    word = get_random_word()
    game_over = False
    attempts = 0
    while not game_over:
        guess = get_guess()
        if guess=='IQUIT':
            print(f'Word: {word}')
            print(f'You quit after {attempts} attempts!')
            game_over=True
        else:
            attempts +=1
            bulls, cows = check(word, guess)
            print(f'{bulls} Bulls & {cows} Cows\n')
            if bulls==4:
                print(f'You win in {attempts} attempts!')
                game_over=True

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print('Error:', str(e))
    input('\nPress Enter To Exit...')