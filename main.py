from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Float, ForeignKey
from flask_wtf import FlaskForm
from wtforms import FloatField, StringField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Email
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import config


app = Flask(__name__)

# LOCAL VARIABLES
app.config["SQLALCHEMY_DATABASE_URI"] = config.DB_URI
app.config['SECRET_KEY'] = config.SECRET_KEY

# LOGIN MANAGER
login_manager = LoginManager()
login_manager.init_app(app)

# DATA BASE
class Base(DeclarativeBase):
    pass
db = SQLAlchemy(model_class=Base)
db.init_app(app)

class MyForm(FlaskForm):
    value = FloatField('New Rating', validators=[DataRequired(), NumberRange(min=0, max=10)])
    submit = SubmitField("Edit")

class AddForm(FlaskForm):
    t = StringField('Title', validators=[DataRequired()])
    a = StringField('Author', validators=[DataRequired()])
    r = FloatField('Rating', validators=[DataRequired(), NumberRange(min=0, max=10)])
    submit = SubmitField("Add")

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = StringField('Password', validators=[DataRequired()])
    submit = SubmitField("Login")

class RegisterForm(LoginForm, FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField("Register")

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000), unique=True)

    books: Mapped[list["NewBook"]] = relationship("NewBook", back_populates="user")

class NewBook(db.Model):
    __tablename__ = "new_books"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250))
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship("User", back_populates="books")

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return db.session.execute(db.select(User).where(User.id==user_id)).scalar()

@app.route('/')
def start():
    return render_template("start.html")

@app.route('/books')
@login_required
def home():
    all_books = current_user.books
    return render_template("index.html", books_list=all_books, user=current_user)

@app.route('/register', methods=["GET", "POST"])
def register():
    reg_form = RegisterForm()
    email = reg_form.email.data
    name = reg_form.name.data
    if reg_form.validate_on_submit():
        if db.session.execute(db.select(User).where(User.email==email)).scalar():
            flash("Email already registered.")
        elif db.session.execute(db.select(User).where(User.name==name)).scalar():
            flash("Name already being used.")
        else:
            user = User(name=name, email=email, password=generate_password_hash(reg_form.password.data, method='pbkdf2', salt_length=8))
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for("home"))
    return render_template("register.html", form=reg_form)
@app.route('/login', methods=["GET", "POST"])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = db.session.execute(db.select(User).where(login_form.email.data==User.email)).scalar()
        if user:
            if check_password_hash(user.password,login_form.password.data):
                login_user(user)
                return redirect(url_for("home"))
        flash("Email or password doesn't match.")
    return render_template("login.html", form=login_form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('start'))

@app.route('/edit/<id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    book = db.session.execute(db.select(NewBook).where(NewBook.id==id)).scalar()
    form_edit = MyForm()
    if not book or book.user_id!=current_user.id:
        return redirect(url_for("home"))
    if form_edit.validate_on_submit():
        book.rating = form_edit.value.data
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit.html", book=book, form=form_edit)

@app.route('/delete/<id>')
@login_required
def delete(id):
    book = db.session.execute(db.select(NewBook).where(NewBook.id==id)).scalar()
    if book and book.user_id==current_user.id:
        db.session.delete(book)
        db.session.commit()
    return redirect(url_for('home'))



@app.route("/add", methods=['GET', 'POST'])
@login_required
def add():
    form_add = AddForm()
    if form_add.validate_on_submit():
        if not db.session.execute(db.select(NewBook).where(form_add.t.data==NewBook.title)).scalar():
            b = NewBook(title=form_add.t.data, author=form_add.a.data, rating=form_add.r.data, user_id=current_user.id)
            db.session.add(b)
            db.session.commit()
            return redirect(url_for('home'))
        else:
            flash("Book already registered.")
    return render_template("add.html", form=form_add)


if __name__ == "__main__":
    app.run(debug=True)

