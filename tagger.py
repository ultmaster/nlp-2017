import nltk
import pylab
from nltk.corpus import brown


brown_tagged_sents = brown.tagged_sents(categories='news')
size = int(len(brown_tagged_sents) * 0.9)
train_sents = brown_tagged_sents[:size]
test_sents = brown_tagged_sents[size:]

fd = nltk.FreqDist(brown.words(categories='news'))
cfd = nltk.ConditionalFreqDist(brown.tagged_words(categories='news'))
x = 1
xes, y1, y2, y3 = [], [], [], []
while x < 4.1:
    most_freq_words = fd.most_common(int(pow(10, x)))
    likely_tags = dict((word, cfd[word].max()) for (word, _) in most_freq_words)
    baseline_tagger = nltk.UnigramTagger(model=likely_tags)
    baseline_tagger_2 = nltk.BigramTagger(brown_tagged_sents, backoff=baseline_tagger)
    baseline_tagger_3 = nltk.TrigramTagger(brown_tagged_sents, backoff=baseline_tagger_2)
    xes.append(int(pow(10, x)))
    y1.append(baseline_tagger.evaluate(test_sents))
    y2.append(baseline_tagger_2.evaluate(test_sents))
    y3.append(baseline_tagger_3.evaluate(test_sents))
    print(x)
    x += 0.1


line1, = pylab.plot(xes, y1, '-bo', label='Unigram', linewidth=1, markersize=2)
line2, = pylab.plot(xes, y2, '-ro', label='Bigram', linewidth=1, markersize=2)
line3, = pylab.plot(xes, y3, '-go', label='Trigram', linewidth=1, markersize=2)
pylab.legend(handles=[line1, line2, line3])
pylab.xlim([10, 10000])
pylab.ylim([0, 1])
pylab.xlabel('Size of dictionary')
pylab.ylabel('Evaluation')
pylab.title('Tagger Performance related to -grams and dict-size')
pylab.savefig("tagger.eps")
