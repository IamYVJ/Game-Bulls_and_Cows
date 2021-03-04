import json
from english_words import english_words_alpha_set

dictionary = {}

with open('allwords.json') as f:
    dictionary = json.loads(f.read())

wordslist = []
for word in english_words_alpha_set:
    if len(word)==4:
        wordslist.append(word.upper())

for alpha in dictionary:
    index = 0
    while index<len(dictionary[alpha]):
        if dictionary[alpha][index] in wordslist:
            index+=1
        else:
            del dictionary[alpha][index]


with open('words.json', 'w') as f:
    f.write(json.dumps(dictionary, indent=4))
