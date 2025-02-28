from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from quiz import app
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False)
    passhash = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(32), nullable=False)
    dob = db.Column(db.String(32), nullable=True)
    qualification = db.Column(db.String(32), nullable=True)
    is_admin=db.Column(db.Boolean,nullable=False,default=False)


    @property
    def password(self):
        raise AttributeError('Password is secret')
    
    @password.setter
    def password(self, password):
        self.passhash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.passhash, password)


class Subject(db.Model):
    __tablename__='subject'
    id=db.Column(db.Integer,primary_key=True)
    sub_name=db.Column(db.String(32),unique=True,nullable=False)
    description=db.Column(db.String(512),nullable=False)
    chapters = db.relationship('Chapter', backref='subject', lazy=True)


class Chapter(db.Model):
    __tablename__='chapter'
    id=db.Column(db.Integer,primary_key=True)
    sub_id=db.Column(db.Integer,db.ForeignKey('subject.id'),nullable=False)
    chapter_name=db.Column(db.String(32),unique=True,nullable=False)
    description=db.Column(db.String(512),nullable=False)
    quiz = db.relationship('Quiz', backref='chapter', lazy=True)

class Quiz(db.Model):
    __tablename__='quiz'
    id=db.Column(db.Integer,primary_key=True)
    chapter_id=db.Column(db.Integer,db.ForeignKey('chapter.id'),nullable=False)
    date_of_quiz=db.Column(db.Date,nullable=False)
    time_duration=db.Column(db.Interval,nullable=False)
    questions = db.relationship('Questions', backref='quiz', lazy=True)

class Questions(db.Model):
    __tablename__='questions'
    id=db.Column(db.Integer,primary_key=True)
    quiz_id=db.Column(db.Integer,db.ForeignKey('quiz.id'),nullable=False)
    q_statement=db.Column(db.String(512),nullable=False)
    options=db.Column(db.String(1024),nullable=False)

class Scores(db.Model):
    __tablename__='scores'
    id=db.Column(db.Integer,primary_key=True)
    quiz_id=db.Column(db.Integer,db.ForeignKey('quiz.id'),nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    date_of_quiz=db.Column(db.Date,nullable=False)
    time_duration=db.Column(db.Time,nullable=False)


with app.app_context():
    db.create_all()
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin=User(username='admin',password='admin',full_name='admin',is_admin=True)
        db.session.add(admin)
        db.session.commit()