import random
import nltk
import math
import pylab
import jieba
from sklearn.svm import LinearSVC
from nltk.classify.scikitlearn import SklearnClassifier
from collections import Counter
from sqlalchemy import Column, String, Integer, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class User(Base):
    def __init__(self, uid, name, description, sex, vote, related):
        self.uid = uid
        self.name = name
        self.description = description
        self.sex = sex
        self.vote = vote
        self.related = related

    __tablename__ = 'users'
    uid = Column(String(50), primary_key=True)
    name = Column(String(50))
    description = Column(String(80))
    sex = Column(Integer)
    vote = Column(Integer)
    related = Column(Integer)

engine = create_engine('sqlite:///./spider.db', echo=False)
DBSession = sessionmaker(bind=engine)
Base.metadata.create_all(engine)


def get_log_feature(number):
    return int(math.log10(number+1))


def get_high_vote_feature(number):
    return 1 if number > 50 else 0


def gender_features(word):
    return {'last_letter': word[-1],
            'last_second_letter': word[-2:],
            # 'first_letter': word[0]
    }

def gender_description_features(description):
    features = dict()
    if description:
        for word in list(jieba.cut(description)):
            if word.strip() != "":
                features['contains(%s)' % word.strip()] = True
    return features


def gender_features_with_description(word, description):
    features = gender_features(word)
    features.update(gender_description_features(description))
    return features


# Name and sex (Naive Bayes)
def name_features():
    session = DBSession()
    users = session.query(User).filter(User.sex != 0).all()
    print(len(users))
    random.shuffle(users)
    names = [(user.name, 'male' if user.sex == 1 else 'female') for user in users]
    featuresets = [(gender_features(n), g) for (n, g) in names]
    train_len = len(featuresets) // 10
    train_set, test_set = featuresets[train_len:], featuresets[:train_len]
    dev_set = names[:train_len]
    # classifier = nltk.MaxentClassifier.train(train_set)
    classifier = nltk.NaiveBayesClassifier.train(train_set)
    # classifier = SklearnClassifier(LinearSVC()).train(train_set)
    for (name, ans) in dev_set:
        guess = classifier.classify(gender_features(name))
        if guess != ans:
            print("correct=%-8s guess=%-8s name=%-30s" % (ans, guess, name))
    print(nltk.classify.accuracy(classifier, test_set))
    classifier.show_most_informative_features(10)
    session.close()


# Name and (sex and description) (Naive Bayes)
def name_features_with_description():
    session = DBSession()
    users = session.query(User).filter(User.sex != 0).all()
    random.shuffle(users)
    names = [(user.name, user.description, 'male' if user.sex == 1 else 'female') for user in users]
    featuresets = [(gender_features_with_description(n, d), g) for (n, d, g) in names]
    train_len = len(featuresets) // 10
    train_set, test_set = featuresets[train_len:], featuresets[:train_len]
    dev_set = names[:train_len]
    # classifier = nltk.MaxentClassifier.train(train_set)
    classifier = nltk.NaiveBayesClassifier.train(train_set)
    for (name, description, ans) in dev_set:
        guess = classifier.classify(gender_features_with_description(name, description))
        if guess != ans:
            print("correct=%-8s guess=%-8s name=%-30s description=%-30s" % (ans, guess, name, description))
    print(nltk.classify.accuracy(classifier, test_set))
    classifier.show_most_informative_features(10)
    session.close()


# Vote Graph
def vote_counting():
    session = DBSession()
    users = session.query(User).all()
    counter = Counter()
    for user in users:
        counter[math.log10(user.vote + 1)] += 1
    sum_count = 0
    x, y = [], []
    pylab.clf()
    for k in sorted(counter.keys()):
        sum_count += counter[k]
        x.append(k)
        y.append(sum_count)
    pylab.xlim([0, max(x)])
    pylab.ylim([0, max(y) * 1.2])
    pylab.xlabel('Logarithm (base 10) of votes')
    pylab.ylabel('Accumulating users')
    pylab.plot(x, y, '-', linewidth=1)
    pylab.savefig('vote_counting.eps')
    session.close()


# Related Users Graph
def related_counting():
    session = DBSession()
    users = session.query(User).all()
    counter = Counter()
    for user in users:
        counter[user.related + 1] += 1
    sum_count = 0
    x, y = [], []
    pylab.clf()
    for k in sorted(counter.keys()):
        sum_count += counter[k]
        x.append(k)
        y.append(sum_count)
        if k > 100:
            break
    pylab.xlim([0, 100])
    pylab.ylim([0, max(y) * 1.2])
    pylab.xlabel('Related users (not working for > 100)')
    pylab.ylabel('Accumulating users')
    pylab.plot(x, y, '-', linewidth=1)
    pylab.savefig('related_counting.eps')
    session.close()


# Vote and description (SVC)
def vote_features():
    session = DBSession()
    users = session.query(User).filter(User.description is not None).all()
    random.shuffle(users)
    names = [(user.description, get_log_feature(user.vote)) for user in users]
    featuresets = [(gender_description_features(d), v) for (d, v) in names]
    train_set, test_set = featuresets[1000:], featuresets[:1000]
    dev_set = names[:1000]
    classifier = SklearnClassifier(LinearSVC())
    classifier.train(train_set)
    for (description, ans) in dev_set:
        guess = classifier.classify(gender_description_features(description))
        if guess != ans:
            print("correct=%-8d guess=%-8d description=%-30s" % (ans, guess, description))
    print(nltk.classify.accuracy(classifier, test_set))
    # classifier.show_most_informative_features(10)
    session.close()


# Vote and description (detailed and Bayes)
def old_vote_features():
    session = DBSession()
    users = session.query(User).filter(User.description is not None).all()
    random.shuffle(users)
    names = [(user.description, str(get_log_feature(user.vote))) for user in users]
    featuresets = [(gender_description_features(d), v) for (d, v) in names]
    train_set, test_set = featuresets[500:], featuresets[:500]
    dev_set = names[:500]
    # classifier = nltk.MaxentClassifier.train(train_set)
    classifier = nltk.NaiveBayesClassifier.train(train_set)
    for (description, ans) in dev_set:
        guess = classifier.classify(gender_description_features(description))
        if guess != ans:
            print("correct=%-8s guess=%-8s description=%-30s" % (ans, guess, description))
    print(nltk.classify.accuracy(classifier, test_set))
    classifier.show_most_informative_features(10)
    session.close()


if __name__ == '__main__':
    vote_features()