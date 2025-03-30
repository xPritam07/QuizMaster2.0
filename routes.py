from flask import render_template, request, redirect, flash, url_for, session
from functools import wraps
from models import db, User, Subject, Chapter, Questions, Scores, UserEnrollment
from quiz import app 
from datetime import datetime, timedelta

def auth_required(func):
    @wraps(func)
    def inner(*args,**kwargs):
        if 'user_id' not in session:
            flash('Please login to continue')
            return redirect(url_for('login_page'))
        return func(*args,**kwargs)
    return inner

def admin_required(func):
    @wraps(func)
    def inner(*args,**kwargs):
        if "user_id" not in session:
            flash('You need to login first')
            return redirect(url_for('login_page'))
        user=User.query.get(session['user_id'])
        if not user.is_admin:
            flash("You are not a autorised personel.")
            return redirect(url_for('login_page'))
        return func(*args,**kwargs)
    return inner

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
    if username=='' or password=='':
        flash('UserName and Password can not be empty.')
        return redirect(url_for('login_page'))
    if not user:
        flash("User does not exist.")
        return redirect(url_for('login_page'))
    if not user.check_password(password):
        flash("Incorrect password.")
        return redirect(url_for('login_page'))
    session['user_id']=user.id
    if user.is_admin:
        return redirect(url_for('admin_dashboard'))
    else:
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
        flash('UserName and Password can not be empty.','danger')
        return redirect(url_for('register_page'))
    if User.query.filter_by(username=username).first():
        flash('User already exists.')
        return redirect(url_for('register_page'))
    user=User(username=username, full_name=full_name,password=password, dob=dob, qualification=qualification)
    db.session.add(user)
    db.session.commit()
    flash('Successful Registration.','success')
    return redirect(url_for('login_page'))

@app.route('/admin')
@admin_required
def admin_dashboard():
    user=User.query.get(session['user_id'])
    subjects=Subject.query.all()
    return render_template('admin_dashboard.html', user = user, subjects=subjects)


@app.route('/subject')
@admin_required
def add_subject():
    return render_template('add_subject.html', user=User.query.get(session['user_id']))

@app.route('/subject',methods=['POST'])
@admin_required
def add_subject_post():
    sub_name=request.form['sub_name']
    description=request.form['description']
    subject=Subject.query.filter_by(sub_name=sub_name).first()
    if not subject:
        subject=Subject(sub_name=sub_name,description=description)
        db.session.add(subject)
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/subject/<int:id>/show')
@admin_required
def show_subject(id):
    subject=Subject.query.filter_by(id=id).first()
    if not subject:
        flash("Subject not found!",'danger')
        return redirect(url_for("admin_dashboard"))
    chapters=Chapter.query.filter_by(sub_id=id).all()
    return render_template("subject_details.html",chapters=chapters,subject=subject)


@app.route('/add/chapter/<int:id>')
@admin_required
def add_chapter(id):
    subject = Subject.query.get_or_404(id)
    return render_template('add_chapter.html',id=id,subject=subject)


@app.route('/add/chapter/<int:id>', methods=['POST'])
@admin_required
def add_chapter_post(id):
    chapter_name = request.form['chapter_name']
    description = request.form['description']

    chapter = Chapter(chapter_name=chapter_name, description=description, sub_id=id)
    db.session.add(chapter)
    db.session.commit()
    return redirect(url_for('show_subject', id=id))


@app.route('/subject/<int:id>/delete')
@admin_required
def delete_subject(id):
    subject = Subject.query.get_or_404(id)
    db.session.delete(subject)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))


@app.route('/students')
@admin_required
def students():
    students = User.query.filter_by(is_admin=False).all()
    return render_template('student_details.html', students=students)

@app.route('/add/question/<int:id>')
@admin_required
def add_questions(id):
    chapter = Chapter.query.get(id)
    return render_template('add_questions.html', chapter=chapter)

@app.route('/add/questions/<int:id>', methods=['POST'])
@admin_required
def add_questions_post(id):
    q_statement = request.form['q_statement']
    option_a = request.form['option1']
    option_b = request.form['option2']
    option_c = request.form['option3']
    option_d = request.form['option4']
    correct_answer = request.form['answer']

    question = Questions(q_statement=q_statement, option_a=option_a, option_b=option_b, option_c=option_c, option_d=option_d, correct_answer=correct_answer, chapter_id=id)
    db.session.add(question)
    db.session.commit()
    return redirect(url_for('show_subject', id=id))

@app.route('/dashboard') 
@auth_required
def student_dashboard():
    user=User.query.get(session['user_id'])
    enrollments = user.enrollments
    return render_template('student_dashboard.html',user=user,enrollments=enrollments)


@app.route('/course/registration', methods=['GET', 'POST'])
@auth_required
def course_registration():
    user = User.query.get(session['user_id'])

    if request.method == 'GET':
        all_subjects = Subject.query.all()
        enrolled_subjects = {enrollment.subject_id for enrollment in user.enrollments}
        available_subjects = [subject for subject in all_subjects if subject.id not in enrolled_subjects]
        return render_template('afterlogin_coursepage.html', subjects=available_subjects)

    if request.method == 'POST':
        subject_id = request.form.get('subject_id')
        existing_enrollment = UserEnrollment.query.filter_by(user_id=user.id, subject_id=subject_id).first()
        if existing_enrollment:
            return redirect(url_for('course_registration'))
        enrollment = UserEnrollment(user_id=user.id, subject_id=subject_id)
        db.session.add(enrollment)
        db.session.commit()
        return redirect(url_for('student_dashboard'))

@app.route('/chapters/<int:id>')
@auth_required
def show_chapter(id):
    subject = Subject.query.get_or_404(id)
    chapters = Chapter.query.filter_by(sub_id=id).all()
    return render_template('show_chapter.html', subject=subject, chapters=chapters, id=id)

@app.route('/quiz/<int:id>')
@auth_required
def take_quiz(id):
    chapter = Chapter.query.get_or_404(id)
    questions = Questions.query.filter_by(chapter_id=id).all()
    return render_template('student_quiz.html', chapter=chapter, questions=questions, id=chapter.sub_id)


@app.route('/quiz/<int:chapter_id>/submit', methods=['POST'])
@auth_required
def submit_quiz(chapter_id): 
    user = User.query.get(session['user_id'])
    chapter = Chapter.query.get_or_404(chapter_id)
    questions = Questions.query.filter_by(chapter_id=chapter_id).all()
    quiz_duration = 300  

    score = 0
    for question in questions:
        user_answer = request.form.get(f"q{question.id}")
        if user_answer == str(question.correct_answer):
            score += 1
    new_score = Scores(user_id=user.id, chapter_id=chapter.id, score=score, date_of_quiz=str(datetime.now().date()), 
                       time_duration=str(timedelta(seconds=quiz_duration)))
    db.session.add(new_score)
    db.session.commit()

    return redirect(url_for('student_dashboard'))

@app.route('/unregister/<int:id>')
@auth_required
def unregister(id):
    user = User.query.get(session['user_id'])
    enrollment = UserEnrollment.query.filter_by(user_id=user.id, subject_id=id).first()
    if enrollment:
        db.session.delete(enrollment)
        db.session.commit()
    return redirect(url_for('student_dashboard'))

@app.route('/delete/chapter/<int:id>')
@admin_required
def delete_chapter(id):
    chapter = Chapter.query.get(id)
    subject_id = chapter.sub_id
    db.session.delete(chapter)
    db.session.commit()
    return redirect(url_for('show_subject', id=subject_id))

@app.route('/remove/<int:id>')
@admin_required
def remove_student(id):
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('students'))

@app.route('/logout')
def logout():
    session.pop('user_id',None)
    flash('Loged out Successfully!','success')
    return redirect(url_for('login_page'))