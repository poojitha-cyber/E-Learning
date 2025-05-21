from inizio import db,login_manager
from inizio import bcrypt
from flask_login import UserMixin
from datetime import datetime
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
class User(db.Model,UserMixin):
    id=db.Column(db.Integer(),primary_key=True)
    username=db.Column(db.String(length=50), nullable=False, unique=True)
    email_address=db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash=db.Column(db.String(length=60), nullable=False)
    courses_enrolled=db.Column(db.Integer(),default=0)
    items=db.relationship('Item', backref='owned_user', lazy=True)

    @property
    def password(self):
        raise self.password
    @password.setter
    def password(self,plain_text_pasword):
        self.password_hash= bcrypt.generate_password_hash(plain_text_pasword).decode('utf-8')
    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)
class Item(db.Model):
    id=db.Column(db.Integer(),primary_key=True)
    code=db.Column(db.String(length=50), nullable=False, unique=True)
    name=db.Column(db.String(length=50), nullable=False, unique=True)
    modules=db.Column(db.Integer(), nullable=False)
    owner=db.Column(db.Integer(), db.ForeignKey('user.id')) 
class Enrollment(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'))
    course_id=db.Column(db.Integer,db.ForeignKey('item.id'))
    date_enrolled=db.Column(db.DateTime,default=datetime.utcnow)
class Question(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    course_id=db.Column(db.Integer,db.ForeignKey('item.id'),nullable=False)
    question_text=db.Column(db.String(length=500),nullable=False)
    option1=db.Column(db.String(length=200),nullable=False)
    option2=db.Column(db.String(length=200),nullable=False)
    option3=db.Column(db.String(length=200),nullable=False)
    option4=db.Column(db.String(length=200),nullable=False)
    correct_option=db.Column(db.String(length=200),nullable=False)
class TestResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Assuming you have User model
    course_id = db.Column(db.Integer, db.ForeignKey('item.id'))  # Assuming your course table is Item
    correct = db.Column(db.Integer)
    incorrect = db.Column(db.Integer)
    unattempted = db.Column(db.Integer)
    total = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='test_results')
    course = db.relationship('Item', backref='test_results')
