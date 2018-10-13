from flask_sqlalchemy import SQLAlchemy
from abc import ABCMeta, abstractmethod
from sqlalchemy import func


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
        server_default=func.now(),
        onupdate=func.now()
    )


class DBRepr:

    def __repr__(self):

        attrs = [
            f'{attr}={getattr(self, attr)}'
            for attr in self.repr_attrs
            if getattr(self, attr)
        ]

        return f"<{self.repr_title} {' '.join(attrs)}>"


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


class ArtMedium(BaseArtTag, db.Model):
    """Mediums.

    >>> ArtMedium('oil paint')
    <ArtMedium code=oil-paint>
    >>> ArtMedium('pastels', 'past')
    <ArtMedium code=past>
    """

    __tablename__ = 'artmediums'
    repr_title = 'ArtMedium'


class ArtGenre(BaseArtTag, db.Model):

    __tablename__ = 'artgenres'
    repr_title = 'ArtGenre'


class BasePerson(DBRepr):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.String(64), nullable=False)
    desc = db.Column(db.Text)
    repr_attrs = ['name']
    repr_title = 'BasePerson'


class Artist(BasePerson):

    __tablename__ = 'artists'
    repr_title = 'Artist'


class Image(CRUDTimeMixin, DBRepr, db.Model):
    """An image."""

    __tablename__ = 'images'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    path = db.Column(db.String, nullable=False)

    def __init__(self, path):
        self.path = path


class Artwork(CRUDTimeMixin, db.Model):
    """A single piece of art."""

    __tablename__ = 'artworks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    desc = db.Column(db.Text)

    main_img_id = db.Column(db.Integer, db.ForeignKey('images.id'))
    main_img = db.relationship('Image')

    mediums = db.relationship(
        'ArtMedium',
        secondary=artworks_artmediums_table,
        backref='artworks'
    )
    genres = db.relationship(
        'ArtGenre',
        secondary=artworks_artgenres_table,
        backref='artworks'
    )
    artists = db.relationship(
        'Artist',
        secondary=artworks_artists_table,
        backref='artworks'
    )
    images = db.relationship(
        'Image',
        secondary='artworkimages'
    )

    def __init__(self, title, **kwargs):
        self.title = title
        for arg, val in kwargs.items():
            if arg in self.__dict__:
                self.__dict__[arg] = val


class ArtworkInfo(BaseArtMeta):
    value = db.Column(db.String(64))


class ArtworkImage(ArtworkInfo, db.Model):

    __tablename__ = 'artworkimages'

    title = db.Column(db.String(80))
    caption = db.Column(db.Text)

    artwork_id = db.Column(db.Integer, db.ForeignKey('artworks.id'))
    artwork = db.relationship(Artwork)

    image_id = db.Column(db.Integer, db.ForeignKey('images.id'))
    image = db.relationship(Image)


