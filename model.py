from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


# Base classes
class BaseArtTag(db.Model):

    code = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(80))
    desc = db.Column(db.Text, nullable=True)

    def __init__(self, name, code=None):

        self.name = name
        self.code = code if code else name[:10]

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.code}>'

    def __str__(self):
        return self.name


class BaseArtMeta(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.String(64), nullable=False)

    artwork_id = db.Column(db.Integer, db.ForeignKey('artworks.id'))
    artwork = db.relationship('artworks', backref='metadata')


class BasePerson(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.String(64), nullable=False)
    desc = db.Column(db.Text)


class CRUDTimeMixin:
    date_created = db.Column(db.Date, nullable=True)
    date_updated = db.Column(
        db.DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )


# Many to many tables
artworks_artmediums_table = db.Table(
    'artworks_artmediums', db.Model.metadata,
    db.Column('artwork_id', db.Integer, db.ForeignKey('artworks.id')),
    db.Column('artmediums_id', db.String, db.ForeignKey('artmediums.code'))
)

artworks_artists_table = db.Table(
    'artworks_artists', db.Model.metadata,
    db.Column('artwork_id', db.Integer, db.ForeignKey('artworks.id')),
    db.Column('artist_id', db.Integer, db.ForeignKey('artists.id'))
)


# Database objects
class ArtMedium(BaseArtTag):

    __tablename__ = 'artmediums'


class ArtGenre(BaseArtTag):

    __tablename__ = 'artgenres'


class Artist(BasePerson):

    __tablename__ = 'artists'


class Artwork(CRUDTimeMixin, db.Model):

    __tablename__ = 'artworks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    desc = db.Column(db.Text)

    main_img_id = db.Column(db.Integer, db.ForeignKey('artworkimages.id'))
    main_img = db.relationship('ArtworkImage')

    mediums = db.relationship(
        'ArtMedium',
        secondary=artwork_artmedium_table,
        backref='artworks'
    )
    genres = db.relationship(
        'ArtGenre',
        secondary=artwork_artgenres_table,
        backref='artworks'
    )
    artists = db.relationship(
        'Artist',
        secondary=artwork_artist_table,
        backref='artworks'
    )

    def __init__(self, title, **kwargs):
        self.title = title
        for arg, val in kwargs.items():
            if arg in self.__dict__:
                self.__dict__[arg] = val



class ArtworkInfo(BaseArtworkMeta):
    value = db.Column(db.String(64))


class ArtworkImage(ArtworkInfo):

    __tablename__ = 'artworkimages'

    title = db.Column(db.String(80))
    path = db.Column(db.String, nullable=False)
    caption = db.Column(db.Text)

    artwork = db.relationship(Artwork, backref='images')

