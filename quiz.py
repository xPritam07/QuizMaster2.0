from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///quizmaster.db'
import models

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

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

if __name__ =='__main__':
    app.run(host='0.0.0.0',port=5501,debug=True)