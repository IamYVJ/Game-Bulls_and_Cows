
import json

data = {}

with open('words.txt') as f:
    lines = f.readlines()
    for line in lines:
        if line!='':
            alpha = line[0]
            line = line.strip()
            words = line.split()
            data[alpha] = words

with open('words.json', 'w') as f:
    f.write(json.dumps(data, indent=4))