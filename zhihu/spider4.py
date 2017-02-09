import requests
import random
import json
from bs4 import BeautifulSoup
from collections import deque
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


engine = create_engine('sqlite:///./spider.db', echo=False)
DBSession = sessionmaker(bind=engine)

new_engine = create_engine('sqlite:///./spider4.db', echo=False)
session_loader = sessionmaker(bind=new_engine)
Article.metadata.create_all(new_engine)


user_agent = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56."
                            "0.2924.87 Safari/537.36"}


if __name__ == "__main__":
    session = DBSession()
    users = session.query(User).all()
    random.shuffle(users)
    dq = deque(user.uid for user in users)
    queue = deque()
    counter = 0
    while len(dq) > 0:
        user = dq.popleft()
        try:
            html = requests.get("https://www.zhihu.com/people/%s/answers" % (user),
                                headers=user_agent).text
            soup = BeautifulSoup(html, "lxml")
            data_state = json.loads(soup.find(id="data").attrs['data-state'])
            answers_dict = data_state['entities']['answers']
            new_list = list(filter(lambda x: x is not None, answers_dict))
            try:
                user_vote = data_state['entities']['users'][user]["voteupCount"]
            except Exception:
                user_vote = 0
            for item in new_list:
                vote = answers_dict[item]["voteupCount"]
                content = BeautifulSoup(answers_dict[item]["content"], "html.parser").get_text()
                counter += 1
                with open("spider4.html", "w") as f:
                    f.write(str(counter))
                try:
                    session = session_loader()
                    session.add(Article(item, content, vote, user_vote))
                    session.commit()
                    session.close()
                except Exception as e:
                    with open("spider4.html", "w") as f:
                        f.write(str(counter))
        except Exception as e:
            with open("spider4.html", "w") as f:
                f.write(str(counter))
