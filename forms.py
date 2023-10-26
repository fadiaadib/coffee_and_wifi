from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, BooleanField, IntegerField
from wtforms.validators import DataRequired


class AddCafeForm(FlaskForm):
    name = StringField(label='Name', validators=[DataRequired()])
    map_url = StringField(label='Map URL', validators=[DataRequired()])
    img_url = StringField(label='Image URL', validators=[DataRequired()])
    location = StringField(label='Location', validators=[DataRequired()])
    has_sockets = BooleanField(label='Has sockets', validators=[])
    has_toilet = BooleanField(label='Has toilet', validators=[])
    has_wifi = BooleanField(label='Has WiFi', validators=[])
    can_take_calls = BooleanField(label='Can take calls', validators=[])
    seats = IntegerField(label='# of seats', validators=[DataRequired()])
    coffee_price = StringField(label='Coffee price', validators=[DataRequired()])
    submit = SubmitField(label='Add')
