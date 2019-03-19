# To manually clean the dictionary from removing the words

import re

words = re.findall(r'\w+', open('dictionary.txt').read().lower())

words2 = []

for x in words:
    if len(x) <= 2:
        print(x)
        if input() == 'y':
            words2.append(x)
    else:
        words2.append(x)

open('dictionary-new.txt', 'w').write('\n'.join(words2))
