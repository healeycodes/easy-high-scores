from sqlalchemy import Column, Integer, String
from highscores.database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    public_key = Column(String(length=50))

    def __init__(self, public_key=''):
        self.public_key = public_key
    
    def __repr__(self):
        return '<User %r>' % (self.public_key)

class Highscore(Base):
    __tablename__ = 'highscores'
    id = Column(Integer, primary_key=True)
    uuid = Column(String(length=50))
    user = Column(String(length=50))
    name = Column(String(length=50))
    score = Column(String(length=50))

    def __init__(self, user='', name='', score='', uuid=''):
        self.user = user
        self.name = name
        self.score = score
        self.uuid = uuid
    
    def __repr__(self):
        return '<Highscore %r>' % (self.name)