from datetime import datetime
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(30), nullable=True)
    role = db.Column(db.String(30), nullable=False, default='candidate')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    resumes = db.relationship('Resume', backref='user', lazy=True, cascade='all, delete-orphan')
    recommendations = db.relationship('Recommendation', backref='user', lazy=True, cascade='all, delete-orphan')

    def get_id(self):
        return str(self.user_id)

    def __repr__(self):
        return f'<User {self.name}>'


class Resume(db.Model):
    __tablename__ = 'resumes'

    resume_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    resume_file = db.Column(db.String(255), nullable=False)
    resume_text = db.Column(db.Text, nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)

    skills = db.relationship('ResumeSkill', backref='resume', lazy=True, cascade='all, delete-orphan')
    recommendations = db.relationship('Recommendation', backref='resume', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Resume {self.resume_id}>'


class Skill(db.Model):
    __tablename__ = 'skills'

    skill_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    skill_name = db.Column(db.String(120), unique=True, nullable=False)
    skill_category = db.Column(db.String(80), nullable=False, default='Technical')

    resume_links = db.relationship('ResumeSkill', backref='skill', lazy=True)
    job_links = db.relationship('JobSkill', backref='skill', lazy=True)

    def __repr__(self):
        return f'<Skill {self.skill_name}>'


class ResumeSkill(db.Model):
    __tablename__ = 'resume_skills'

    resume_skill_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.resume_id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.skill_id'), nullable=False)
    skill_level = db.Column(db.String(50), nullable=True, default='detected')

    def __repr__(self):
        return f'<ResumeSkill {self.resume_id}:{self.skill_id}>'


class Job(db.Model):
    __tablename__ = 'jobs'

    job_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    job_title = db.Column(db.String(150), nullable=False)
    company_name = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    required_skills = db.Column(db.Text, nullable=False)
    experience = db.Column(db.String(100), nullable=False)
    salary = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    skills = db.relationship('JobSkill', backref='job', lazy=True, cascade='all, delete-orphan')
    recommendations = db.relationship('Recommendation', backref='job', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Job {self.job_title}>'


class JobSkill(db.Model):
    __tablename__ = 'job_skills'

    job_skill_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.job_id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.skill_id'), nullable=False)

    def __repr__(self):
        return f'<JobSkill {self.job_id}:{self.skill_id}>'


class Recommendation(db.Model):
    __tablename__ = 'recommendations'

    recommendation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.resume_id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.job_id'), nullable=False)
    match_score = db.Column(db.Float, nullable=False, default=0.0)
    recommendation_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Recommendation {self.job_id}>'
