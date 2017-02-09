# coding=utf-8
import requests
from bs4 import BeautifulSoup
import re
import json
import time
import random
import shutil
import uuid
from collections import deque
from sqlalchemy import Column, String, Integer, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

fout = open("spider.html", "w", buffering=1, encoding='utf-8')
user_agent = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56."
                            "0.2924.87 Safari/537.36"}


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


def get_user_list(uid, page):
    tid = 1
    total = []
    while True:
        new_list = []
        try:
            html = requests.get("https://www.zhihu.com/people/%s/%s?page=%d" % (uid, page, tid),
                                headers=user_agent).text
            soup = BeautifulSoup(html, "lxml")
            data_state = json.loads(soup.find(id="data").attrs['data-state'])
            new_list = list(filter(lambda x: x is not None, data_state['people'][page + 'ByUser'][uid]['ids']))
        except Exception as e:
            print(e)
        total += new_list
        if tid > 4 or len(new_list) == 0:
            break
        tid += 1
    random.shuffle(total)
    return total[:12]


def get_info(uid):
    related_users = []
    try:
        html = requests.get('https://www.zhihu.com/people/%s/answers' % uid,
                            headers=user_agent).text
        soup = BeautifulSoup(html, "lxml")
        name = soup.select(".ProfileHeader-title .ProfileHeader-name")[0].string

        description = soup.select(".ProfileHeader-title .ProfileHeader-headline")[0].string
        if soup.select(".ProfileHeader-contentBody svg.Icon--female"):
            sex = 2
        elif soup.select(".ProfileHeader-contentBody svg.Icon--male"):
            sex = 1
        else:
            sex = 0
        vote = 0
        for item in soup.select(".Profile-sideColumnItem .IconGraf"):
            item_string = item.text
            if item_string and re.search(r"获得 \d+ 次赞同", item_string):
                vote = int(re.search(r'\d+', re.search(r"获得 \d+ 次赞同", item_string).group()).group())
                break
        related_users = get_user_list(uid, 'followers') + get_user_list(uid, 'following')
        random.shuffle(related_users)
        try:
            session = DBSession()
            new_user = User(uid, name, description, sex, vote, len(related_users))
            session.add(new_user)
            session.commit()
            session.close()
        except Exception as e:
            fout.write('Some collision just happened.')
        fout.write("%s %s %s %d %d %d %s\n" %
            (uid, name, description, sex, vote, len(related_users), time.strftime("%Y/%m/%d %H:%M:%S")))
    except Exception as e:
        print(e)
        time.sleep(3)
    return related_users


if __name__ == "__main__":
    import sys
    user_set = set()
    dq = deque()
    count = 0
    dq.append(sys.argv[1])
    while len(dq) > 0:
        user = dq.popleft()
        if user in user_set:
            continue
        try:
            user_set.add(user)
            for t in get_info(user):
                dq.append(t)
                if len(dq) > 10000:
                    break
            count += 1
            if count % 10 == 0:
                fout.write("%d\n" % count)
            if count % 1000 == 0:
                shutil.copyfile('./spider.db', './spider-%s.db' % (uuid.uuid1()))
            if count > 300000:
                break
        except Exception:
            pass
