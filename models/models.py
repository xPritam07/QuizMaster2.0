from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from quiz import app
from sqlalchemy.engine import Engine
from sqlalchemy import event

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False)
    passhash = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(32), nullable=False)
    dob = db.Column(db.String(32), nullable=True)
    qualification = db.Column(db.String(32), nullable=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    enrollments = db.relationship('UserEnrollment', back_populates='user', cascade="all, delete", passive_deletes=True)
    scores = db.relationship('Scores', back_populates='user', cascade="all, delete", passive_deletes=True)

    @property
    def password(self):
        raise AttributeError('Password is secret')

    @password.setter
    def password(self, password):
        self.passhash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.passhash, password)

class Subject(db.Model):
    __tablename__ = 'subject'
    id = db.Column(db.Integer, primary_key=True)
    sub_name = db.Column(db.String(32), unique=True, nullable=False)
    description = db.Column(db.String(512), nullable=False)

    chapters = db.relationship('Chapter', back_populates='subject', cascade="all, delete", passive_deletes=True)
    enrollments = db.relationship('UserEnrollment', back_populates='subject', cascade="all, delete", passive_deletes=True)


class UserEnrollment(db.Model):
    __tablename__ = 'enrollments'
    enrollment_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id', ondelete='CASCADE'), nullable=False)

    user = db.relationship('User', back_populates='enrollments')
    subject = db.relationship('Subject', back_populates='enrollments')

class Chapter(db.Model):
    __tablename__ = 'chapter'
    id = db.Column(db.Integer, primary_key=True)
    sub_id = db.Column(db.Integer, db.ForeignKey('subject.id', ondelete='CASCADE'), nullable=False)
    chapter_name = db.Column(db.String(32), unique=True, nullable=False)
    description = db.Column(db.String(512), nullable=False)

    subject = db.relationship('Subject', back_populates='chapters')
    questions = db.relationship('Questions', back_populates='chapter', cascade="all, delete", passive_deletes=True)
    scores = db.relationship('Scores', back_populates='chapter', cascade="all, delete", passive_deletes=True)


class Questions(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id', ondelete='CASCADE'), nullable=False)
    q_statement = db.Column(db.String(512), nullable=False)
    option_a = db.Column(db.String(512), nullable=False)
    option_b = db.Column(db.String(512), nullable=False)
    option_c = db.Column(db.String(512), nullable=False)
    option_d = db.Column(db.String(512), nullable=False)
    correct_answer = db.Column(db.String(512), nullable=False)

    chapter = db.relationship('Chapter', back_populates='questions')

class Scores(db.Model):
    __tablename__ = 'scores'
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    date_of_quiz = db.Column(db.String(128), nullable=False)
    time_duration = db.Column(db.String(128), nullable=False)

    user = db.relationship('User', back_populates='scores')
    chapter = db.relationship('Chapter', back_populates='scores')

with app.app_context(): 
    db.create_all()
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin=User(username='admin',password='admin',full_name='admin',is_admin=True)
        db.session.add(admin)
        db.session.commit()