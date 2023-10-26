from flask import Flask, jsonify, render_template, request, url_for, redirect
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

from forms import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SECRET_KEY'] = '4deda00663522c95fe4739c87c8e4d40f07eb2ab30780f4c4d8b8a69b2268e28'
# -> generated through python -c 'import secrets; print(secrets.token_hex())'

# Connect to Database
db = SQLAlchemy()
db.init_app(app)

# Init Bootstrap
Bootstrap5(app)


# Database initialization
class Cafe(db.Model):
    __tablename__ = 'cafe'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    seats = db.Column(db.Integer, nullable=False)
    coffee_price = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()


# APIs
@app.route('/cafes', methods=['GET'])
def get_cafes():
    result = db.session.execute(db.select(Cafe).order_by(Cafe.name))
    all_cafes = result.scalars()
    return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])


@app.route('/add_cafe', methods=['GET', 'POST'])
def add_cafe():
    form = AddCafeForm()
    if form.validate_on_submit():
        try:
            cafe = Cafe(
                name=form.name.data,
                map_url=form.map_url.data,
                img_url=form.img_url.data,
                location=form.location.data,
                has_sockets=form.has_sockets.data,
                has_toilet=form.has_toilet.data,
                has_wifi=form.has_wifi.data,
                can_take_calls=form.can_take_calls.data,
                seats=form.seats.data,
                coffee_price=form.coffee_price.data,
            )
            db.session.add(cafe)
            db.session.commit()
        except IntegrityError:
            return jsonify(error={'Cannot Add Record': 'Error adding cafe'})
        else:
            return redirect(url_for('home'))

    return render_template('add_cafe.html', form=form)


# Website pages
@app.route('/')
def home():
    cafes = get_cafes()
    return render_template('index.html', cafes=cafes.json['cafes'])


if __name__ == '__main__':
    app.run(debug=True, port=5000)
