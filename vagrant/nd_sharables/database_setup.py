from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, scoped_session
from sqlalchemy import create_engine
from datetime import datetime

engine = create_engine('postgresql://localhost:5432/mydb')
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    """Initialize DB setup."""
    Base.metadata.create_all(bind=engine)


def get_db_session():
    """Getter function for DB session."""
    return db_session


class User(Base):
    __tablename__ = "users"

    _id = Column(Integer, primary_key=True)
    username = Column(String(80))
    fullname = Column(String(80))
    email = Column(String(80))
    github_url = Column(String(80))
    github_access_token = Column(String(200))
    avatar_url = Column(String(200))

    def __init__(self, github_access_token):
        self.github_access_token = github_access_token


class Project(Base):
    __tablename__ = "projects"

    _id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    url = Column(String(200), nullable=False)
    created = Column(DateTime(), default=datetime.utcnow)
    thumbnail = Column(String(200), default="/static/images/dummy.png")
    nd_category = Column(String(80), nullable=False)
    p_category = Column(String(8), nullable=False)
    description = Column(String(500))
    author = Column(Integer, ForeignKey('users._id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Returns object data in easily serialized format"""
        return {
            "name": self.name,
            "project_url": self.url,
            "project_id": self._id,
            "created": self.created,
            "thumbnail_url": self.thumbnail,
            "nd_category": self.nd_category,
            "project_category": self.p_category,
            "description": self.description,
            "author_id": self.author,
        }


class Comment(Base):
    __tablename__ = "comments"

    _id = Column(Integer, primary_key=True)
    content = Column(String(500), nullable=False)
    created = Column(DateTime(), default=func.datetime.utcnow)
    author = Column(Integer, ForeignKey('users._id'))
    project_id = Column(Integer, ForeignKey('projects._id'))
    user = relationship(User)
    project = relationship(Project)
