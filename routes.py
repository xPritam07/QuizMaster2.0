from flask import render_template, request, redirect, flash, url_for
from models import db, User, Subject, Chapter, Quiz, Questions, Scores
from quiz import app 


@app.route('/home')
@app.route('/')
def home_page():
    return render_template('index.html')

@app.route('/courses')
def course_page():
    return render_template('course.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/login',methods=['POST'])
def login_post():
    username= request.form.get('username')
    password= request.form.get('password')
    user= User.query.filter_by(username=username).first()
    if not user:
        flash("User does not exist.")
        return redirect(url_for('login_page'))
    if not user.check_password(password):
        flash("Incorrect password.")
        return redirect(url_for('login_page'))
    #successful login
    flash('Login Successful!')
    return redirect(url_for('home_page'))

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')
