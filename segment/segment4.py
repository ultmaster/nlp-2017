from random import randint
import nltk
import math
import pylab
import jieba
import numpy as np
from sklearn.svm import LinearSVC
from nltk.classify.scikitlearn import SklearnClassifier
import os
import pickle


def get_features(word, wordlist):
    feature = {'prev_word': word}
    if isinstance(wordlist, str):
        string = wordlist
    else:
        string = ''.join(wordlist)
    for i in range(1, 6):
        feature['next_word_%d' % i] = string[:i]
    return feature


from sys import stderr
print('Loading Dictionary...', file=stderr)
with open('./spider5.dict', 'rb') as f:
    featuresets = pickle.load(f)
print('Machine Learning...', file=stderr)
train_set, test_set = featuresets[500:], featuresets[:500]
classifier = nltk.NaiveBayesClassifier.train(train_set)
print(nltk.classify.accuracy(classifier, test_set))
print('Machine Learning Done!', file=stderr)


def segment(text):
    prev_word = ""
    result = []
    while len(text) > 0:
        res = classifier.classify(get_features(prev_word, text))
        result.append(text[:res])
        text = text[res:]
    return result


if __name__ == '__main__':
    text = "jintianwozailushangjiandaoleyizhishouji"
    print(segment(text))
