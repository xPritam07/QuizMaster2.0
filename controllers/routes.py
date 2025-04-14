from flask import render_template, request, redirect, flash, url_for, session
from functools import wraps
from models.models import db, User, Subject, Chapter, Questions, Scores, UserEnrollment
from quiz import app 
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import uuid

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

@app.route('/edit_subject/<int:id>', methods=['GET', 'POST'])
def edit_subject(id):
    subject = Subject.query.get_or_404(id)

    if request.method == 'POST':
        subject.sub_name = request.form['sub_name']
        subject.description = request.form['description']
        db.session.commit()
        flash('Subject updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('edit_subject.html', subject=subject)

@app.route('/subject/<int:id>/show')
@admin_required
def show_subject(id):
    subject=Subject.query.filter_by(id=id).first()
    if not subject:
        flash("Subject not found!",'danger')
        return redirect(url_for("admin_dashboard"))
    chapters=Chapter.query.filter_by(sub_id=id).all()
    return render_template("subject_details.html",chapters=chapters,subject=subject)

@app.route('/chapter/<int:chapter_id>/questions')
@admin_required
def show_questions(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    questions = Questions.query.filter_by(chapter_id=chapter_id).all()
    return render_template('show_quiz.html', chapter=chapter, questions=questions)

@app.route('/question/edit/<int:question_id>', methods=['GET', 'POST'])
@admin_required
def edit_question(question_id):
    question = Questions.query.get_or_404(question_id)

    if request.method == 'POST':
        question.q_statement = request.form['q_statement']
        question.option_a = request.form['option_a']
        question.option_b = request.form['option_b']
        question.option_c = request.form['option_c']
        question.option_d = request.form['option_d']
        question.correct_answer = request.form['correct_answer']

        db.session.commit()
        flash('Question updated successfully!', 'success')
        return redirect(url_for('show_questions', chapter_id=question.chapter_id))

    return render_template('edit_quiz.html', question=question)

@app.route('/question/delete/<int:question_id>')
@admin_required
def delete_question(question_id):
    question = Questions.query.get_or_404(question_id)
    chapter_id = question.chapter_id
    db.session.delete(question)
    db.session.commit()
    flash('Question deleted successfully!', 'success')
    return redirect(url_for('show_questions', chapter_id=chapter_id))


@app.route('/add/question/<int:subject_id>/<int:chapter_id>')
@admin_required
def add_questions(subject_id, chapter_id):
    chapter = Chapter.query.get(chapter_id)
    subject=Subject.query.get(subject_id)
    return render_template('add_questions.html', chapter=chapter, subject=subject)

@app.route('/add/questions/<int:subject_id>/<int:chapter_id>', methods=['POST'])
@admin_required
def add_questions_post(subject_id, chapter_id):
    q_statement = request.form['q_statement']
    option_a = request.form['option1']
    option_b = request.form['option2']
    option_c = request.form['option3']
    option_d = request.form['option4']
    correct_answer = request.form['answer']

    question = Questions(
        q_statement=q_statement,
        option_a=option_a,
        option_b=option_b,
        option_c=option_c,
        option_d=option_d,
        correct_answer=correct_answer,
        chapter_id=chapter_id
    )
    db.session.add(question)
    db.session.commit()
    subject=Subject.query.get(subject_id)
    chapter=Chapter.query.get(chapter_id)
    return redirect(url_for('show_subject', id=subject.id))

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

@app.route('/student_info/<int:student_id>')
@admin_required
def student_info(student_id):
    user = User.query.get(student_id)
    enrollments = user.enrollments

    # Get highest score per chapter
    all_scores = Scores.query.filter_by(user_id=user.id).all()
    highest_scores = {}

    for score in all_scores:
        chapter_id = score.chapter_id
        if chapter_id not in highest_scores or score.score > highest_scores[chapter_id]:
            highest_scores[chapter_id] = score.score

    chapter_labels = []
    chapter_scores = []

    for chapter_id, score in highest_scores.items():
        chapter = Chapter.query.get(chapter_id)
        if chapter.chapter_name == None:
            chapter_labels.append("Invaild Chapter")
        else:
            chapter_labels.append(f"{chapter.chapter_name}")
        chapter_scores.append(score)

    # Generate plot only if there is data
    plot_filename = None
    if chapter_scores:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(chapter_labels, chapter_scores, color='skyblue')
        ax.set_title('Highest Score per Chapter')
        ax.set_xlabel('Chapters')
        ax.set_ylabel('Score')
        plt.xticks(rotation=30, ha='right')
        plt.tight_layout()

        # Save the plot to static folder
        plot_filename = f"{uuid.uuid4().hex}.png"
        plot_path = os.path.join('static', 'plots', plot_filename)
        os.makedirs(os.path.dirname(plot_path), exist_ok=True)
        plt.savefig(plot_path)
        plt.close()

    return render_template('student_info.html',
                           student=user,
                           enrollments=enrollments,
                           histogram_path=plot_path)

@app.route('/summary')
@auth_required
def student_summary():
    user = User.query.get(session['user_id'])

    # Get highest score per chapter
    all_scores = Scores.query.filter_by(user_id=user.id).all()
    highest_scores = {}

    for score in all_scores:
        chapter_id = score.chapter_id
        if chapter_id not in highest_scores or score.score > highest_scores[chapter_id]:
            highest_scores[chapter_id] = score.score

    chapter_labels = []
    chapter_scores = []

    for chapter_id, score in highest_scores.items():
        chapter = Chapter.query.get(chapter_id)
        if chapter.chapter_name == None:
            chapter_labels.append("Invaild Chapter")
        else:
            chapter_labels.append(f"{chapter.chapter_name}")
        chapter_scores.append(score)

    # Generate plot only if there is data
    plot_filename = None
    if chapter_scores:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(chapter_labels, chapter_scores, color='skyblue')
        ax.set_title('Highest Score per Chapter')
        ax.set_xlabel('Chapters')
        ax.set_ylabel('Score')
        plt.xticks(rotation=30, ha='right')
        plt.tight_layout()

        # Save the plot to static folder
        plot_filename = f"{uuid.uuid4().hex}.png"
        plot_path = os.path.join('static', 'plots', plot_filename)
        os.makedirs(os.path.dirname(plot_path), exist_ok=True)
        plt.savefig(plot_path)
        plt.close()

    return render_template('student_summary.html', plot_filename=plot_filename)

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
    new_score = Scores(user_id=user.id, chapter_id=chapter.id, score=score, date_of_quiz=str(datetime.now()), 
                       time_duration=str(timedelta(seconds=quiz_duration)))
    db.session.add(new_score)
    db.session.commit()

    return redirect(url_for('results'))

@app.route('/results')
@auth_required
def results():
    user = User.query.get(session['user_id'])
    latest_score = Scores.query.filter_by(user_id=user.id).order_by(Scores.date_of_quiz.desc()).first()
    
    if not latest_score:
        flash("No quiz attempts found.", "warning")
        return redirect(url_for('student_dashboard'))

    return render_template('score.html', user=user, score=latest_score)



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