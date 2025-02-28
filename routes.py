from flask import render_template, request, redirect, flash, url_for, session
from models import db, User, Subject, Chapter, Quiz, Questions, Scores
from quiz import app 
session={}

def check_session():
    if 'user_id' not in session:
        flash('Please login to continue')
        return False
    return True
    

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
    if username=='' or password=='':
        flash('UserName and Password can not be empty.')
        return redirect(url_for('login_page'))
    user= User.query.filter_by(username=username).first()
    if not user:
        flash("User does not exist.")
        return redirect(url_for('login_page'))
    if not user.check_password(password):
        flash("Incorrect password.")
        return redirect(url_for('login_page'))
    #successful login
    session['user_id']=user.id
    return redirect(url_for('student_dashboard'))
        

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/register',methods=['POST'])
def register_post():
    username=request.form['username']
    password=request.form['password']
    full_name=request.form['full_name']
    dob=request.form['date']
    qualification=request.form['qualification']
    if username=='' or password=='':
        flash('UserName and Password can not be empty.')
        return redirect(url_for('register_page'))
    if User.query.filter_by(username=username).first():
        flash('User already exists.')
        return redirect(url_for('register_page'))
    user=User(username=username, full_name=full_name,password=password, dob=dob, qualification=qualification)
    db.session.add(user)
    db.session.commit()
    flash('Successful Registration.')
    return redirect(url_for('login_page'))


@app.route('/dashboard')
def student_dashboard():
    if not check_session():
        return redirect(url_for('login_page'))
    return render_template('student_dashboard.html')

@app.route('/course/quiz')
def course_login():
    if not check_session():
        return redirect(url_for('login_page'))
    return render_template('afterlogin_coursepage.html')

@app.route('/logout')
def logout():
    session.pop('user_id',None)
    flash('Loged out Successfully!')
    return redirect(url_for('login_page'))

