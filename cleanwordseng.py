import json
import enchant

engcheck = enchant.Dict("en_US")

dictionary = {}

with open('allwords.json') as f:
    dictionary = json.loads(f.read())

for alpha in dictionary:
    index = 0
    while index<len(dictionary[alpha]):
        if engcheck.check(dictionary[alpha][index]):
            index+=1
        else:
            del dictionary[alpha][index]


with open('words.json', 'w') as f:
    f.write(json.dumps(dictionary, indent=4))
