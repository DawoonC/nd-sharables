from sqlalchemy import Column, ForeignKey, Integer, String, DATETIME, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, scoped_session
from sqlalchemy import create_engine

engine = create_engine('sqlite:///ndSharables.db')
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

    id = Column(Integer, primary_key=True)
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

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    url = Column(String(200), nullable=False)
    created = Column(DATETIME, default=func.current_timestamp())
    thumbnail = Column(String(200), default="/static/images/dummy.png")
    nd_category = Column(String(80), nullable=False)
    p_category = Column(String(8), nullable=False)
    description = Column(String(200))
    author = Column(Integer, ForeignKey('users.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Returns object data in easily serialized format"""
        return {
            "name": self.name,
            "project_url": self.url,
            "project_id": self.id,
            "created": self.created,
            "thumbnail_url": self.thumbnail,
            "nd_category": self.nd_category,
            "project_category": self.p_category,
            "description": self.description,
            "author_id": self.author,
        }


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)
    content = Column(String(500), nullable=False)
    created = Column(DATETIME, default=func.current_timestamp())
    author = Column(Integer, ForeignKey('users.id'))
    project_id = Column(Integer, ForeignKey('projects.id'))
    user = relationship(User)
    project = relationship(Project)
