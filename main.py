from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import FloatField, StringField, SubmitField
from wtforms.validators import DataRequired, NumberRange
import config

import config

app = Flask(__name__)

class Base(DeclarativeBase):
    pass

class MyForm(FlaskForm):
    value = FloatField('New Rating', validators=[DataRequired(), NumberRange(min=0, max=10)])
    submit = SubmitField("Edit")

class AddForm(FlaskForm):
    t = StringField('Title', validators=[DataRequired()])
    a = StringField('Author', validators=[DataRequired()])
    r = FloatField('Rating', validators=[DataRequired(), NumberRange(min=0, max=10)])
    submit = SubmitField("Add")


#local variables
app.config["SQLALCHEMY_DATABASE_URI"] = config.DB_URI
app.config['SECRET_KEY'] = config.SECRET_KEY

db = SQLAlchemy(model_class=Base)
db.init_app(app)

class NewBook(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    all_books = list(db.session.execute(db.select(NewBook).order_by(NewBook.title)).scalars())
    return render_template("index.html", books_list=all_books)

@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    form_edit = MyForm()
    result = db.session.execute(db.select(NewBook).where(NewBook.id == id)).scalar()
    if form_edit.validate_on_submit():
        result.rating = form_edit.value.data
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit.html", book=result, form=form_edit)

@app.route('/delete/<id>')
def delete(id):
    book = db.session.execute(db.select(NewBook).where(NewBook.id == id)).scalar()
    db.session.delete(book)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/add", methods=['GET', 'POST'])
def add():
    form_add = AddForm()
    if form_add.validate_on_submit():
        b = NewBook(title=form_add.t.data, author=form_add.a.data, rating=form_add.r.data)
        db.session.add(b)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("add.html", form=form_add)


if __name__ == "__main__":
    app.run(debug=True)

