from model import db, Artwork
from flask_api import FlaskAPI, exceptions
from flask import request


app = FlaskAPI(__name__)
app.debug = True
app.secret_key = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///yoldasstudiolab'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


@app.route('/artwork/<int:key>', methods=['GET',])
def artwork(key):
    """Get or update artwork."""

    a = Artwork.get(key).to_dict_repr()

    if not a:
        exceptions.NotFound()

    return a


@app.route("/", methods=['GET', 'POST'])
def notes_list():
    """
    List or create notes.
    """
    if request.method == 'POST':
        note = str(request.data.get('text', ''))
        idx = max(notes.keys()) + 1
        notes[idx] = note
        return note_repr(idx), status.HTTP_201_CREATED

    # request.method == 'GET'
    return [note_repr(idx) for idx in sorted(notes.keys())]


if __name__ == '__main__':

    db.app = app
    db.init_app(app)
    app.run()

