import json
from spellchecker import SpellChecker

spell = SpellChecker()

dictionary = {}

with open('allwords.json') as f:
    dictionary = json.loads(f.read())

for alpha in dictionary:
    index = 0
    while index<len(dictionary[alpha]):
        word = dictionary[alpha][index]
        if word==spell.correction(word).upper():
            index+=1
        else:
            del dictionary[alpha][index]


with open('words.json', 'w') as f:
    f.write(json.dumps(dictionary, indent=4))
