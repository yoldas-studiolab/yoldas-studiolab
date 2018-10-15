from flask_sqlalchemy import SQLAlchemy
import json
from datetime import datetime


db = SQLAlchemy()


# Base classes

class BaseArtMeta:

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), nullable=False)
    artwork_id = db.Column(db.Integer, db.ForeignKey('artworks.id'))


class CRUDTimeMixin:
    date_created = db.Column(db.Date, nullable=True)
    date_updated = db.Column(
        db.DateTime(timezone=True),
        server_default=db.func.now(),
        onupdate=db.func.now()
    )


class JSONMixin:
    def to_dict_repr(self):

        public_attrs = {
            attr: val
            for attr, val in self.__dict__.items()
            if not attr.startswith('_')
        }

        d = {}
        for attr, val in public_attrs.items():
            if isinstance(val, db.Model):
                d[attr] = val.to_dict_repr()
            elif isinstance(val, list):
                d[attr] = [
                    v.to_dict_repr()
                    for v in val
                ]
            elif isinstance(val, datetime):
                d[attr] = val.isoformat()
            else:
                d[attr] = val

        return d


class DBRepr:

    def __repr__(self):

        attrs = [
            f'{attr}={getattr(self, attr)}'
            for attr in self.repr_attrs
            if getattr(self, attr)
        ]

        return f"<{self.repr_title} {' '.join(attrs)}>"


# Database objects
class BaseArtTag(DBRepr):
    """Tags are for many-to-many relationships."""

    code = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(80))
    desc = db.Column(db.Text, nullable=True)
    repr_attrs = ['code']
    repr_title = 'BaseArtTag'

    def __init__(self, name, code=None, desc=None):

        self.name = name
        self.code = code if code else name[:10].replace(' ', '-')
        if desc:
            self.desc = desc

    def __str__(self):
        return self.name


class ArtMedium(JSONMixin ,BaseArtTag, db.Model):
    """Mediums.

    >>> ArtMedium('oil paint')
    <ArtMedium code=oil-paint>
    >>> ArtMedium('pastels', 'past')
    <ArtMedium code=past>
    """

    __tablename__ = 'artmediums'
    repr_title = 'ArtMedium'


class ArtGenre(JSONMixin, BaseArtTag, db.Model):

    __tablename__ = 'artgenres'
    repr_title = 'ArtGenre'


class BasePerson(DBRepr):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.String(64), nullable=False)
    desc = db.Column(db.Text)
    repr_attrs = ['name']
    repr_title = 'BasePerson'


class Artist(BasePerson, db.Model):

    __tablename__ = 'artists'
    repr_title = 'Artist'


class Image(JSONMixin, CRUDTimeMixin, DBRepr, db.Model):
    """An image."""

    __tablename__ = 'images'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    path = db.Column(db.String, nullable=False)

    def __init__(self, path):
        self.path = path


class Artwork(JSONMixin, CRUDTimeMixin, DBRepr, db.Model):
    """A single piece of art."""

    __tablename__ = 'artworks'
    repr_title = 'Artwork'
    repr_attrs = ['id', 'title']

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    desc = db.Column(db.Text)

    main_img_id = db.Column(db.Integer, db.ForeignKey('images.id'))
    main_img = db.relationship('Image')

    mediums = db.relationship(
        'ArtMedium',
        secondary='artworks_artmediums',
        backref='artworks'
    )
    genres = db.relationship(
        'ArtGenre',
        secondary='artworks_artgenres',
        backref='artworks'
    )
    artists = db.relationship(
        'Artist',
        secondary='artworks_artists',
        backref='artworks'
    )
    images = db.relationship(
        'Image',
        secondary='artworkimages'
    )

    joins = {'mediums', 'genres', 'artists', 'images',}

    def __init__(self, title, **kwargs):
        self.title = title
        for arg, val in kwargs.items():
            if arg in self.__dict__:
                self.__dict__[arg] = val

    @classmethod
    def get(cls, key, opts=None):
        """Get via key"""

        q = cls.query
        if not opts:
            opts = cls.joins

        joinedload = [
            db.joinedload(opt)
            for opt in opts
            if opt in cls.joins
        ]

        q = q.options(*joinedload)

        return q.get(key)



class ArtworkInfo(BaseArtMeta):
    value = db.Column(db.String(64))


class ArtworkImage(JSONMixin, ArtworkInfo, db.Model):

    __tablename__ = 'artworkimages'

    title = db.Column(db.String(80))
    caption = db.Column(db.Text)

    artwork_id = db.Column(db.Integer, db.ForeignKey('artworks.id'))
    artwork = db.relationship(Artwork)

    image_id = db.Column(db.Integer, db.ForeignKey('images.id'))
    image = db.relationship(Image)


# Many to many tables
artworks_artmediums_table = db.Table(
    'artworks_artmediums', db.Model.metadata,
    db.Column('artwork_id', db.Integer, db.ForeignKey('artworks.id')),
    db.Column('artmediums_code', db.String, db.ForeignKey('artmediums.code'))
)

artworks_artists_table = db.Table(
    'artworks_artists', db.Model.metadata,
    db.Column('artwork_id', db.Integer, db.ForeignKey('artworks.id')),
    db.Column('artist_id', db.Integer, db.ForeignKey('artists.id'))
)

artworks_artgenres_table = db.Table(
    'artworks_artgenres', db.Model.metadata,
    db.Column('artwork_id', db.Integer, db.ForeignKey('artworks.id')),
    db.Column('genre_code', db.String, db.ForeignKey('artgenres.code'))
)

if __name__ == '__main__':
    from flask import Flask

    app = Flask(__name__)
    app.debug = True
    app.secret_key = 'secret'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///yoldasstudiolab'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)

