import os
import os.path

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy import create_engine

from mel.marian.util import filename_safety

Session = sessionmaker(autoflush=False)

class ShowDB(object):
  session = False
  db_existed = None

  @classmethod
  def connect(cls, seriesname, echo=False):
    db_filename = filename_safety("%s.sqlite" % (seriesname))
    cls.db_existed = os.path.exists(db_filename)
    engine = create_engine("sqlite:///%s" % db_filename, echo=echo)
    if not cls.db_existed:
      Base.metadata.create_all(engine)
    Session.configure(bind=engine)
    cls.session = Session()
  @classmethod
  def commit(cls):
    cls.session.commit()
  @classmethod
  def delete(cls, obj):
    cls.session.delete(obj)

class FindOrCreateMixin(object):
  @classmethod
  def find(cls, **kwargs):
    return ShowDB.session.query(cls).filter_by(**kwargs).first()
  @classmethod
  def find_or_create(cls, **kwargs):
    '''
    Creates an object or returns the object if exists
    credit to Kevin @ StackOverflow
    from: http://stackoverflow.com/questions/2546207/does-sqlalchemy-have-an-equivalent-of-djangos-get-or-create
    '''
    instance = ShowDB.session.query(cls).filter_by(**kwargs).first()
    if instance:
        return instance
    instance = cls(**kwargs)
    ShowDB.session.add(instance)
    ShowDB.commit()
    return instance

Base = declarative_base(cls=FindOrCreateMixin)

class Episode(Base):
  __tablename__ = 'episodes'

  id = Column(Integer, primary_key=True)
  name = Column(String)
  episode_no = Column(Integer)
  season_id = Column(Integer, ForeignKey('seasons.id'))
  air_date = Column(DateTime)
  description = Column(Text)

  season = relationship("Season", back_populates="episodes")

  def __repr__(self):
    return "<Episode(episode_no=%s, air_date='%s', name='%s')>" % (
      self.episode_no, self.air_date, self.name)

  def filename(self, extension=".mkv"):
    return filename_safety("{0} - S{1}E{2} - {3}{4}".format(
      self.season.show.name,
      str(self.season.season_no).zfill(2),
      str(self.episode_no).zfill(2),
      self.name,
      extension))

class Season(Base):
  __tablename__ = 'seasons'

  id = Column(Integer, primary_key=True)
  name = Column(String)
  season_no = Column(Integer)
  show_id = Column(Integer, ForeignKey('shows.id'))

  show = relationship("Show", back_populates="seasons")
  episodes = relationship("Episode", back_populates="season", lazy='joined')

  def episode_find_or_create(self, **kwargs):
    return Episode.find_or_create(season_id=self.id, **kwargs)

  def __repr__(self):
    return "<Season(id=%s, season_no=%s, show_id = %s)>" % (
      self.id, self.season_no, self.show_id)

class Show(Base):
  __tablename__ = 'shows'

  id = Column(Integer, primary_key=True)
  name = Column(String)
  seasons = relationship("Season", back_populates="show", lazy='joined')

  def season_find_or_create(self, **kwargs):
    return Season.find_or_create(show_id=self.id, **kwargs)

  def __repr__(self):
    return "<Show(id=%s, name='%s')>" % (
      self.id, self.name)
