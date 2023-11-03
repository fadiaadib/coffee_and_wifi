from functools import wraps

from flask import Flask, jsonify, render_template, url_for, redirect, flash, abort
from flask_bootstrap import Bootstrap5
from flask_login import UserMixin, current_user, login_user, login_required, logout_user, LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_gravatar import Gravatar
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash

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

# Login manager
login_manager = LoginManager()
login_manager.init_app(app)
gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)


# Load user interface
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user and current_user.is_authenticated and current_user.id == 1:
            return f(*args, **kwargs)
        return abort(403)

    return decorated_function


# Database initialization
class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(500), nullable=False)
    type = db.Column(db.String(250), nullable=False)
    cafes = relationship("Cafe", back_populates="author")

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


class Cafe(db.Model):
    __tablename__ = 'cafe'

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    author = relationship("User", back_populates="cafes")

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


@app.route('/add_cafe', methods=['GET', 'POST'])
def add_cafe():
    # Check if the user is logged in
    if not current_user.is_authenticated:
        # User not logged in
        flash('You need to register or login to add a new Cafe')
        return redirect(url_for('login'))

    form = AddCafeForm()
    if form.validate_on_submit():
        try:
            # Create the Cafe object
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
                author=current_user,
            )
            # Add the Cafe object to the database
            db.session.add(cafe)
            db.session.commit()
        except IntegrityError as error:
            # Failed to add the entry into the database
            return jsonify(error=f'Cannot Add Record: {error}')
        else:
            # Cafe addition was successful, go home
            return redirect(url_for('home'))

    return render_template('add_cafe.html', form=form)


# Website pages
@app.route('/')
def home():
    result = db.session.execute(db.select(Cafe).order_by(Cafe.name))
    all_cafes = result.scalars()
    return render_template('index.html', cafes=all_cafes)


@app.route('/register', methods=['GET', 'POST'])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        # Check if the user already exists and show flash error
        check_user = db.session.execute(db.select(User).where(User.email == register_form.email.data)).scalar()
        if check_user:
            flash(f'{register_form.email.data} already exists, try to login instead')
            return redirect(url_for('login'))

        # Create user object
        user = User(
            type='contributor',
            name=register_form.name.data,
            email=register_form.email.data,
            password=generate_password_hash(password=register_form.password.data,
                                            method='pbkdf2:sha256',
                                            salt_length=8),
        )
        db.session.add(user)
        db.session.commit()

        # Login successful
        login_user(user)
        # Goto home
        return redirect(url_for('home'))

    return render_template("register.html", form=register_form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = db.session.execute(db.select(User).where(User.email == login_form.email.data)).scalar()
        # Check if he user does not exist and show a flash error
        if not user:
            flash(f'Sorry, {login_form.email.data} does not exist')
        elif check_password_hash(user.password, login_form.password.data):
            # Login successful
            login_user(user)
            # Goto home
            return redirect(url_for('home'))
        else:
            # Show flash error that the password does not match
            flash(f'Incorrect password for user {login_form.email.data}')

    return render_template("login.html", form=login_form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/blog')
def blog():
    return render_template('blog.html')


if __name__ == '__main__':
    app.run(debug=True, port=5002)
