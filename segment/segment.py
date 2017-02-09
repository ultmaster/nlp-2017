from random import randint
import os
import pickle


if not os.path.exists('./english.pickle'):
    from nltk.corpus import brown
    import nltk
    WORDLIST = nltk.FreqDist([word.lower() for word in brown.words()])
    with open('./english.pickle', 'wb') as f:
        pickle.dump(WORDLIST, f)
else:
    with open('./english.pickle', 'rb') as f:
        WORDLIST = pickle.load(f)


def segment(text, segs):
    words = []
    last = 0
    for i in range(len(segs)):
        if segs[i] == '1':
            words.append(text[last:i+1])
            last = i+1
    words.append(text[last:])
    return words

def evaluate(text, segs):
    words = segment(text, segs)
    text_size = len(words)
    lexicon_size = sum(len(word) + 1 for word in set(words))
    word_size = 0
    for word in set(words):
        word_size += pow(WORDLIST[word.lower()], 0.3)
    return (text_size + lexicon_size) * 3 - word_size * 0.8


def flip(segs, pos):
    return segs[:pos] + str(1-int(segs[pos])) + segs[pos+1:]


def flip_n(segs, n):
    for i in range(n):
        segs = flip(segs, randint(0, len(segs)-1))
    return segs


def anneal(text, segs, iterations, cooling_rate):
    temperature = float(len(segs))
    while temperature > 0.5:
        best_segs, best = segs, evaluate(text, segs)
        for i in range(iterations):
            guess = flip_n(segs, round(temperature))
            score = evaluate(text, guess)
            if score < best:
                best, best_segs = score, guess
        score, segs = best, best_segs
        temperature = temperature / cooling_rate
        print(evaluate(text, segs), segment(text, segs))
    print()
    return segs


print('dictionary load done!')

text = "doyouseethekittyseethedoggydoyoulikethekittylikethedoggy"
# seg1 = "01001001001000010010010000101001000100100001000100100001"
best, segs = evaluate(text, "0" * len(text)), "0" * len(text)
print("test on %d" % 6)
print()
for j in range(3):
    print("attempt %d" % j)
    seg1 = "0" * len(text)
    seg1 = flip_n(seg1, len(text) // 6)
    seg1 = anneal(text, seg1, 5000, 1.1)
    if evaluate(text, seg1) < best:
        best, segs = evaluate(text, seg1), seg1
print(best, segment(text, segs))
print()

