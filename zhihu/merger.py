import os
from sqlalchemy import Column, String, Integer, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
BASE_DIR = os.path.dirname(__file__)


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


if __name__ == '__main__':
    base_engine = create_engine('sqlite:///' + os.path.join(BASE_DIR, 'spider.db'), echo=True)
    print('sqlite:///' + os.path.join(BASE_DIR, 'spider.db'))
    base_DBSession = sessionmaker(bind=base_engine)
    Base.metadata.create_all(base_engine)

    for file in os.listdir(BASE_DIR):
        if file.startswith('spider-'):
            engine = create_engine('sqlite:///' + os.path.join(BASE_DIR, file), echo=False)
            DBSession = sessionmaker(bind=engine)
            Base.metadata.create_all(engine)
            session = DBSession()
            users = session.query(User).all()
            session.close()


            for user in users:
                try:
                    session = base_DBSession()
                    session.add(User(uid=user.uid, name=user.name, description=user.description,
                                     sex=user.sex, vote=user.vote, related=user.related))
                    session.commit()
                    session.close()
                except Exception as e:
                    print(e)

