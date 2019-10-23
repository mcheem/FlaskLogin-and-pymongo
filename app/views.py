from app import app, lm
from pymongo import MongoClient
from flask import request, redirect, render_template, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug import generate_password_hash
from .forms import LoginForm, RegistrationForm
from .user import User


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = app.config['USERS_COLLECTION'].find_one({"_id": form.username.data})
        if user and User.validate_login(user['password'], form.password.data):
            user_obj = User(user['_id'])
            login_user(user_obj)
            flash("Logged in successfully!", category='success')
            return redirect(request.args.get("next") or url_for("write"))
        flash("Wrong username or password!", category='error')
    return render_template('login.html', title='login', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if request.method == 'POST' and form.validate_on_submit():
        collection = MongoClient()["blog"]["users"]
        username = form.username.data
        password = form.password.data
        password_hash = generate_password_hash(password, method='pbkdf2:sha256')
        try:
            collection.insert_one({"_id": username, "password": password_hash})
            flash("User created.", category='success')
            return redirect(url_for('login'))
        except DuplicateKeyError:
            flash("User already present in Database.", category='warning')
            return redirect(url_for('register'))

    return render_template('register.html', title='register', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/write', methods=['GET', 'POST'])
@login_required
def write():
    return render_template('write.html')


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    return render_template('settings.html')


@lm.user_loader
def load_user(username):
    u = app.config['USERS_COLLECTION'].find_one({"_id": username})
    if not u:
        return None
    return User(u['_id'])
