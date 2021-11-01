from flask import Flask, render_template, redirect, url_for, flash, request
from models import db, User, ToDo
from forms import LoginForm, RegisterForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bootstrap import Bootstrap
from flask_login import login_user, LoginManager, login_required, current_user, logout_user
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///todo.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

Bootstrap(app)

################################# DATABASE INITIALIZATION #################################

db.app = app
db.init_app(app)
db.create_all()

################################# USER LOGIN #################################

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


################################# ROUTES #################################

@app.route('/', methods=["GET", "POST"])
def home():
    if request.method == 'POST' and request.form["todo_input"]:
        new_todo = ToDo(
            todo=request.form["todo_input"],
            finished=False,
            author=current_user,
            date=datetime.now().strftime("%B %d %Y")
        )
        db.session.add(new_todo)
        db.session.commit()
    return render_template("todo.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(password=form.password.data, salt_length=8)
        if User.query.filter_by(email=form.email.data).first():
            flash("You already have registered that email, login instead")
            return redirect(url_for("login"))
        else:
            new_user = User(email=form.email.data,
                            name=form.name.data,
                            password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)

            return redirect(url_for("home"))
    return render_template("login-register.html", form=form, register=True)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            flash('That email is not registered, register instead', 'error')
            return redirect(url_for("register"))
        else:
            # Check stored password hash against entered password hashed.
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for("home"))
            else:
                flash("Invalid password")
    return render_template("login-register.html", form=form, register=False)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/finish/<int:todo_id>')
@login_required
def finish_todo(todo_id):
    todo = ToDo.query.get(todo_id)
    if current_user.id == todo.author_id:
        todo.finished = True
        db.session.commit()
    return redirect(url_for("home"))

# edit pa aayusin boii
# @app.route('/edit-id/<int:todo_id>')
# def get_edit_id(todo_id):
#     print(todo_id, "wala")
#     print("wala")
#     session['edit_id'] = todo_id
#     print(session['edit_id'])
#     return redirect(url_for('home'))


@app.route('/edit/<int:todo_id>', methods=["POST"])
@login_required
def edit_todo(todo_id):
    todo = ToDo.query.get(todo_id)
    if request.method == 'POST' and request.form["edit_todo"] and current_user.id == todo.author_id:
        todo.todo = request.form["edit_todo"]
        db.session.commit()
    return redirect(url_for('home'))


@app.route('/delete/<int:todo_id>')
@login_required
def delete_todo(todo_id):
    to_delete = ToDo.query.get(todo_id)
    if current_user.id == to_delete.author_id:
        db.session.delete(to_delete)
        db.session.commit()
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)