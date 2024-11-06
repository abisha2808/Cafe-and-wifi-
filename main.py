from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
import flask_wtf
from flask_wtf import FlaskForm
from sqlalchemy import String, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, SubmitField, TimeField, SelectField,FloatField,BooleanField
from wtforms.validators import DataRequired, URL
import csv

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)


# CREATE DB
class Base(DeclarativeBase):
    pass


# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


class cafe(db.Model):
    __tablename__ = 'cafe'
    id = db.Column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)


class CafeForm(FlaskForm):
    name = StringField('Cafe name', validators=[DataRequired()])
    location = StringField("Location", validators=[DataRequired()])
    map_url = StringField("Map Location", validators=[DataRequired(), URL()])
    img_url = StringField("Image", validators=[DataRequired(), URL()])
    coffee_price = StringField("Coffee price", validators=[DataRequired()],)
    has_wifi = BooleanField("has wifi", validators=[DataRequired()])
    has_socket = BooleanField("has socket", validators=[DataRequired()])
    has_toilet = BooleanField("has toilet", validators=[DataRequired()])
    can_take_call= BooleanField("can take call", validators=[DataRequired()])
    seats = StringField("seats", validators=[DataRequired()])
    submit = SubmitField('Add cafe', render_kw={"class": "btn light-brown-btn"})


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/cafes")
def show_cafe():
    with app.app_context():
        result = db.session.execute(db.select(cafe))
        all_cafe = result.scalars().all()
        return render_template("cafes.html", cafes_list=all_cafe)


@app.route("/cafe/<id>")
def show_details(id):
    cafe_id = id
    with app.app_context():
        show_cafe = db.session.execute(db.select(cafe).where(cafe.id == cafe_id)).scalar()
        return render_template("details.html", cafe=show_cafe)


@app.route('/add', methods=['GET', 'POST'])
def add_cafe():
    form = CafeForm()
    if form.validate_on_submit():
        with app.app_context():
            # Create a new Cafe instance
            new_cafe = cafe(name=form.name.data, location=form.location.data, img_url=form.img_url.data, map_url=form.map_url.data,
                            has_socket=form.has_socket.data, has_wifi=form.has_wifi.data, has_toilet=form.has_toilet.data,
                            can_take_call=form.can_take_call.data, seats=form.seats.data, coffee_price=form.coffee_price.data)
            # Add the new instance to the session
            db.session.add(new_cafe)
            # Commit the session to save the new cafe to the database
            db.session.commit()
        return redirect(url_for('show_cafe'))
    # Exercise:
    # Make the form write a new row into cafe-data.csv
    # with   if form.validate_on_submit()
    return render_template('add_cafe.html', form=form)

@app.route("/search")
def search():
    with app.app_context():
        search_query = request.args.get('query')
        print(search_query)
        # Use the search_query to filter cafes by name
        if search_query:
            # Filter cafes by name using a case-insensitive match
            cafes = cafe.query.filter(cafe.name.ilike(f'%{search_query}%')).all()
        else:
            # If no query is provided, return all cafes or handle it accordingly
            cafes = []
        # Render the search results
        return render_template('search.html', cafes_list=cafes, search_query=search_query)


if __name__ == '__main__':
    app.run(debug=True)
