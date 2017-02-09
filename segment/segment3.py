from random import randint
import os
import pickle
import random
from collections import deque


# if not os.path.exists('./english.pickle'):
#     from nltk.corpus import brown
#     import nltk
#     WORDLIST = nltk.FreqDist([word.lower() for word in brown.words()])
#     with open('./english.pickle', 'wb') as f:
#         pickle.dump(WORDLIST, f)
# else:
#     with open('./english.pickle', 'rb') as f:
#         WORDLIST = pickle.load(f)

with open('./spider2.dict', 'rb') as f:
    WORDLIST = pickle.load(f)


def find_best(text, depth):
    easy_to_find = 0
    best_solution, best_val = 0, -1e9
    if depth <= 2 and text:
        for i in range(len(text)):
            current_val = 0.04 * i + pow(WORDLIST[text[:i+1]], 0.3) + \
                          0.3 * pow(0.8, depth) * find_best(text[i+1:], depth+1)[1]
            easy_to_find += current_val
            if current_val > best_val:
                best_val, best_solution = current_val, i
    return (best_solution, easy_to_find)


def extract_best(text):
    return find_best(text, 1)[0]


def segment_split(text):
    found = []
    working_found = deque()

    strike, last = 0, None
    for it in range(len(text)):
        flow = ''.join(working_found)
        working_found.clear()
        flow += text[it]

        while len(flow) > 0:
            loc = extract_best(flow)
            working_found.append(flow[:loc + 1])
            flow = flow[loc + 1:]
        if working_found[0] != last:
            strike = 1
            last = working_found[0]
        else:
            strike += 1
        if strike >= 4 * len(last):
            found.append(working_found.popleft())

    found += working_found
    return found


if __name__ == '__main__':
    print('dictionary load done!')

    text = "doyouseethekittyseethedoggydoyoulikethekittylikethedoggy"
    # text = "jintianwozailushangjiandaoleyizhishouji"
    # seg1 = "01001001001000010010010000101001000100100001000100100001"
    found = []
    working_found = deque()
    flow = ""

    strike, last = 0, None
    for it in range(len(text)):
        flow = ''.join(working_found)
        working_found.clear()

        flow += text[it]

        while len(flow) > 0:
            loc = extract_best(flow)
            working_found.append(flow[:loc+1])
            flow = flow[loc+1:]
        if working_found[0] != last:
            strike = 1
            last = working_found[0]
        else:
            strike += 1
        if strike >= 4 * len(last):
            found.append(working_found.popleft())

    found += working_found
    print(found)