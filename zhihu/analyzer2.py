import random
import nltk
import math
import pylab
import jieba
import jieba.analyse
import os
import pickle
import numpy as np
from sklearn.svm import LinearSVC
from nltk.classify.scikitlearn import SklearnClassifier
from collections import Counter, defaultdict
from sqlalchemy import Column, String, Integer, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class Article(Base):
    def __init__(self, id, article, vote, user_vote):
        self.id = id
        self.article = article
        self.vote = vote
        self.user_vote = user_vote

    __tablename__ = 'articles'
    id = Column(String(50), primary_key=True)
    article = Column(String)
    vote = Column(Integer)
    user_vote = Column(Integer)


new_engine = create_engine('sqlite:///./spider4.db', echo=False)
session_loader = sessionmaker(bind=new_engine)
Article.metadata.create_all(new_engine)
total_count = 0

with open("BosonNLP_sentiment_score.txt") as f:
    lst = f.readlines()
    sentiment_data = dict()
    for item in lst:
        try:
            wo, sc = item.split()
            sentiment_data[wo] = float(sc)
        except Exception:
            pass


def get_log_feature(number):
    return int(math.log10(number+1))


def cut_analyzer(text):
    global total_count
    total_count += 1
    if total_count % 1000 == 0:
        print(total_count)
    features = {'length': int(len(text) / 100)}
    counter = Counter()
    if text:
        for word in list(jieba.cut(text)):
            if word.strip() != "":
                counter[word.strip()] += 1
    for key in counter.most_common(15):
        if counter[key] < 3:
            break
        features[key] = True
    return features


def keyword_analyzer(text):
    global total_count
    total_count += 1
    if total_count % 1000 == 0:
        print(total_count)
    features = jieba.analyse.extract_tags(text)
    # print(features)
    return dict((feature, True) for feature in features)


def sentiment_analyzer(text):
    global total_count
    total_count += 1
    if total_count % 1000 == 0:
        print(total_count)
    score = 0
    global sentiment_data
    for word in jieba.cut(text):
        score += sentiment_data.get(word, 0) ** 2
    return score / len(text) * 100


def length_analyzer(text):
    return {'length': int(len(text) / 100)}


# Article content and vote
def content_vote_features():
    session = session_loader()
    articles = session.query(Article).all()
    random.shuffle(articles)
    # article_vote = [(article.article, str(get_log_feature(article.vote))) for article in articles]
    article_vote = [(article.article, str(get_log_feature(article.vote))) for article in articles]
    featuresets = [(cut_analyzer(d), v) for (d, v) in article_vote]
    print('Analysis Complete')
    train_len = len(featuresets) // 10
    train_set, test_set = featuresets[train_len:], featuresets[:train_len]
    dev_set = article_vote[:train_len]
    classifier = nltk.NaiveBayesClassifier.train(train_set)
    # classifier = SklearnClassifier(LinearSVC()).train(train_set)
    for (description, ans) in dev_set:
        guess = classifier.classify(cut_analyzer(description))
        if guess != ans:
            print("correct=%-8s guess=%-8s description=%-30s" % (ans, guess, description[:30]))
    print(nltk.classify.accuracy(classifier, test_set))
    # sample = "我不挑 你一般就好 我江西的 你可以是杭州的 你也可以是江西的 96 你别嫌弃我矮172 矮人可以cdx吗 杭州的我能过去陪你过情人节 江西的我能回来看你 要试试吗"
    # print(classifier.classify(cut_analyzer(sample)))
    classifier.show_most_informative_features(10)
    session.close()


def spam_or_not():
    session = session_loader()
    articles = session.query(Article).all()[:50000]
    random.shuffle(articles)
    article_vote = [(article.article, 0 if article.vote > 1 else 1) for article in articles]
    featuresets = [(sentiment_analyzer(d), v) for (d, v) in article_vote]
    print('Analysis Complete')
    train_len = len(featuresets) // 20
    train_set, test_set = featuresets[train_len:], featuresets[:train_len]
    dev_set = article_vote[:train_len]
    classifier = nltk.NaiveBayesClassifier.train(train_set)
    # classifier = SklearnClassifier(LinearSVC()).train(train_set)
    for (description, ans) in dev_set:
        guess = classifier.classify(sentiment_analyzer(description))
        if guess != ans:
            print("correct=%-8s guess=%-8s description=%-30s" % (ans, guess, description[:30]))
    print(nltk.classify.accuracy(classifier, test_set))
    # sample = "我不挑 你一般就好 我江西的 你可以是杭州的 你也可以是江西的 96 你别嫌弃我矮172 矮人可以cdx吗 杭州的我能过去陪你过情人节 江西的我能回来看你 要试试吗"
    # print(classifier.classify(cut_analyzer(sample)))
    classifier.show_most_informative_features(10)
    session.close()


def get_average_of_top(lst, percentage):
    new_lst = sorted(lst, reverse=True)[:int(len(lst)*percentage)]
    return sum(new_lst) / len(new_lst)


# Article length and vote
def length_vote_counting():
    session = session_loader()
    articles = session.query(Article).all()
    random.shuffle(articles)
    articles = articles[:10000]
    x, y = [], []
    for article in articles:
        x.append(len(article.article))
        y.append(article.vote)
    pylab.clf()
    pylab.xlim([0, get_average_of_top(x, 0.05)])
    pylab.ylim([0, get_average_of_top(y, 0.05)])
    pylab.xlabel('Length of articles')
    pylab.ylabel('Votes')
    pylab.scatter(x, y, s=0.2, alpha=0.3)
    pylab.savefig('length_vote_counting.eps')
    session.close()


# User vote and article vote
def user_article_vote():
    session = session_loader()
    articles = session.query(Article).all()
    counter = Counter()
    x, y, s = [], [], []
    for article in articles:
        mx = article.user_vote - article.user_vote % 10
        my = article.vote - article.vote % 10
        counter[(mx, my)] += 1
    for (a, b) in counter.keys():
        x.append(a)
        y.append(b)
        s.append(counter[(a, b)] * 0.05 + 0.1)
    pylab.clf()
    pylab.xlim([0, get_average_of_top(x, 0.05)])
    pylab.ylim([0, get_average_of_top(y, 0.05)])
    pylab.xlabel('Votes for users')
    pylab.ylabel('Votes for articles')
    pylab.scatter(x, y, s=s, alpha=0.3)
    pylab.savefig('user_article_vote_counting.eps')
    session.close()


def user_article_vote_analysis():
    session = session_loader()
    articles = session.query(Article).all()
    counter = Counter()
    vote_all = Counter()
    x, y, w = [], [], []
    for article in articles:
        mx = article.user_vote - article.user_vote % 100
        vote_all[mx] += article.vote
        counter[mx] += 1
    for key in sorted(counter):
        x.append(key)
        y.append(vote_all[key] / counter[key])
        w.append(counter[key])
        print(key, vote_all[key], counter[key])
    x = x[:int(0.3 * len(x))]
    y = y[:int(0.3 * len(y))]
    w = w[:int(0.3 * len(w))]
    s = [0.3 * (math.log(tmp)) for tmp in w]
    yvals = np.polyval(np.polyfit(x, y, 4, w=w), x)
    pylab.clf()
    pylab.xlim([0, get_average_of_top(x, 0.08)])
    pylab.ylim([0, get_average_of_top(y, 0.3)])
    pylab.xlabel('Votes for users')
    pylab.ylabel('Votes for articles')
    pylab.scatter(x, y, s=s, alpha=0.6)
    pylab.plot(x, yvals, 'r')
    pylab.savefig('user_article_vote_counting_6.eps')
    session.close()


def sentiment_analyze():
    session = session_loader()
    articles = session.query(Article).filter(Article.article != "").all()
    random.shuffle(articles)
    sample_articles = random.sample(articles, 100)
    sample_articles = [(sentiment_analyzer(article.article), article.article.split('\n'))
                       for article in sample_articles]
    sample_articles.sort(key=lambda x: x[0])
    for article in sample_articles:
        print(article)
    counter = Counter()
    total_vote = Counter()
    for article in articles:
        if len(article.article) > 0:
            key = sentiment_analyzer(article.article)
            if key > 800:
                print(article.article.split('\n'))
            counter[int(key)] += 1
            total_vote[int(key)] += article.vote
    x, y, w = [], [], []
    for key in sorted(counter):
        x.append(key)
        y.append(total_vote[key] / counter[key])
        w.append(counter[key])
        print(key, total_vote[key] / counter[key], counter[key])
    s = [0.5 * (math.log(tmp) + 1) for tmp in w]
    pylab.clf()
    pylab.xlim(0, 400)
    pylab.ylim(0, 300)
    # pylab.xlim([0, get_average_of_top(x, 0.05)])
    # pylab.ylim(0, get_average_of_top(y, 0.02))
    pylab.xlabel('Sentimental Value')
    pylab.ylabel('Average Vote')
    pylab.scatter(x, y, s=s)
    pylab.savefig('sentimental_vote_6.eps')
    session.close()


def length_analysis():
    session = session_loader()
    articles = session.query(Article).all()
    random.shuffle(articles)
    articles = articles
    counter = Counter()
    total_vote = Counter()
    for article in articles:
        key = int(len(article.article) / 100)
        counter[key] += 1
        total_vote[key] += article.vote
    x, y, w = [], [], []
    for key in sorted(counter):
        x.append(key * 100)
        y.append(total_vote[key] / counter[key])
        w.append(counter[key])
        print(key * 100, total_vote[key] / counter[key], counter[key])
    x = x[:int(0.9 * len(x))]
    y = y[:int(0.9 * len(y))]
    w = w[:int(0.9 * len(w))]
    s = [0.5 * (math.log(tmp) * 3 + 1) for tmp in w]
    y1 = np.polyfit(x, y, 4, w=w)
    yvals = np.polyval(y1, x)
    pylab.clf()
    pylab.xlim([0, get_average_of_top(x, 0.05)])
    pylab.ylim(0, 4000)
    pylab.xlabel('Length of article')
    pylab.ylabel('Average Vote')
    pylab.scatter(x, y, s=s)
    pylab.plot(x, yvals, 'r')
    pylab.savefig('length_analysis_2.eps')
    session.close()


if __name__ == '__main__':
    sentiment_analyze()
