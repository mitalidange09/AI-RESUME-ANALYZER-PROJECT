import logging

import pymysql

from config import Config

logger = logging.getLogger(__name__)

DEFAULT_JOBS = [
    {
        "job_title": "Python Developer",
        "company_name": "Sample Technology Solutions",
        "location": "Pune",
        "description": "Build Python services, REST APIs, and data-backed web applications with code reviews and automated testing.",
        "required_skills": "Python, SQL, Flask, REST API, Git",
        "experience": "0-2 years",
        "salary": "INR 4-8 LPA",
    },
    {
        "job_title": "Junior Python Developer",
        "company_name": "Sample Cloud Works",
        "location": "Remote",
        "description": "Support backend development using Python, Django, databases, unit tests, and collaborative Git workflows.",
        "required_skills": "Python, Django, SQL, Git, REST API",
        "experience": "0-1 years",
        "salary": "INR 3-6 LPA",
    },
    {
        "job_title": "Flask Developer",
        "company_name": "Sample Web Systems",
        "location": "Mumbai",
        "description": "Develop and maintain Flask web applications, backend APIs, SQL data models, and secure integrations.",
        "required_skills": "Python, Flask, SQL, HTML, CSS",
        "experience": "0-2 years",
        "salary": "INR 4-7 LPA",
    },
    {
        "job_title": "Web Developer",
        "company_name": "Sample Digital Studio",
        "location": "Pune",
        "description": "Create responsive websites and connect frontend experiences to accessible backend services.",
        "required_skills": "HTML, CSS, JavaScript, Python, SQL",
        "experience": "0-2 years",
        "salary": "INR 3-6 LPA",
    },
    {
        "job_title": "Full Stack Developer",
        "company_name": "Sample Product Labs",
        "location": "Bengaluru",
        "description": "Deliver full stack product features across browser interfaces, JavaScript applications, APIs, and databases.",
        "required_skills": "JavaScript, HTML, CSS, Python, SQL, Git",
        "experience": "1-3 years",
        "salary": "INR 6-12 LPA",
    },
    {
        "job_title": "Backend Developer",
        "company_name": "Sample Enterprise Apps",
        "location": "Hyderabad",
        "description": "Build reliable backend services, REST APIs, database integrations, and automated tests.",
        "required_skills": "Python, SQL, REST API, Git, Flask",
        "experience": "0-3 years",
        "salary": "INR 5-10 LPA",
    },
    {
        "job_title": "Software Developer",
        "company_name": "Sample Software Group",
        "location": "Pune",
        "description": "Design, implement, debug, and test software features with a cross-functional engineering team.",
        "required_skills": "Python, Java, SQL, Git, Problem Solving",
        "experience": "0-2 years",
        "salary": "INR 4-8 LPA",
    },
    {
        "job_title": "AI/ML Intern",
        "company_name": "Sample Intelligent Systems",
        "location": "Remote",
        "description": "Assist with machine learning experiments, data preparation, Python notebooks, and model evaluation.",
        "required_skills": "Python, Machine Learning, Artificial Intelligence, Pandas, NumPy",
        "experience": "Internship",
        "salary": "INR 15,000-25,000 per month",
    },
    {
        "job_title": "Machine Learning Intern",
        "company_name": "Sample Data Research",
        "location": "Mumbai",
        "description": "Prepare datasets and prototype machine learning models using Python and common data science libraries.",
        "required_skills": "Python, ML, Pandas, NumPy, Scikit-learn",
        "experience": "Internship",
        "salary": "INR 15,000-25,000 per month",
    },
    {
        "job_title": "Data Analyst",
        "company_name": "Sample Analytics Partners",
        "location": "Pune",
        "description": "Query business data, prepare reports, identify trends, and communicate evidence-based insights.",
        "required_skills": "SQL, Python, Excel, Data Analysis, Power BI",
        "experience": "0-2 years",
        "salary": "INR 4-8 LPA",
    },
    {
        "job_title": "Data Science Intern",
        "company_name": "Sample Data Science Co",
        "location": "Bengaluru",
        "description": "Explore datasets, build analytical notebooks, and support predictive modeling experiments.",
        "required_skills": "Python, SQL, Machine Learning, Pandas, NumPy",
        "experience": "Internship",
        "salary": "INR 18,000-30,000 per month",
    },
    {
        "job_title": "Java Developer",
        "company_name": "Sample Business Software",
        "location": "Hyderabad",
        "description": "Implement and maintain Java applications, SQL integrations, automated tests, and API features.",
        "required_skills": "Java, SQL, REST API, Git, Problem Solving",
        "experience": "0-2 years",
        "salary": "INR 4-8 LPA",
    },
    {
        "job_title": "Frontend Developer",
        "company_name": "Sample Interface Studio",
        "location": "Remote",
        "description": "Build accessible, responsive user interfaces and collaborate with design and backend teams.",
        "required_skills": "HTML, CSS, JavaScript, React, Git",
        "experience": "0-2 years",
        "salary": "INR 4-8 LPA",
    },
    {
        "job_title": "SQL Developer",
        "company_name": "Sample Database Services",
        "location": "Pune",
        "description": "Write and optimize SQL queries, support relational database reporting, and validate data quality.",
        "required_skills": "SQL, MySQL, Python, Data Analysis, Excel",
        "experience": "0-2 years",
        "salary": "INR 4-7 LPA",
    },
    {
        "job_title": "Junior Software Engineer",
        "company_name": "Sample Engineering Works",
        "location": "Mumbai",
        "description": "Contribute to engineering projects through coding, debugging, testing, and team communication.",
        "required_skills": "Python, Java, SQL, Git, Communication",
        "experience": "0-1 years",
        "salary": "INR 4-7 LPA",
    },
]


def ensure_database_exists():
    connection = pymysql.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        autocommit=True,
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{Config.DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
            )
        connection.commit()
    finally:
        connection.close()


def initialize_database():
    ensure_database_exists()
    from models import db

    try:
        from app import app

        with app.app_context():
            db.create_all()
            seed_default_jobs()
    except Exception as exc:  # pragma: no cover - startup safety guard
        logger.warning("Database initialization deferred because MySQL is not yet available: %s", exc)


def create_database():
    initialize_database()


def seed_default_jobs():
    from models import Job, db

    if Job.query.count() >= 8:
        return 0

    existing = {
        (job.job_title.strip().casefold(), job.company_name.strip().casefold())
        for job in Job.query.all()
    }
    new_jobs = [
        Job(**job_data)
        for job_data in DEFAULT_JOBS
        if (
            job_data["job_title"].casefold(),
            job_data["company_name"].casefold(),
        )
        not in existing
    ]
    if new_jobs:
        db.session.add_all(new_jobs)
        db.session.commit()
    return len(new_jobs)


def save_resume(filename, score, skills, word_count):
    return {
        "filename": filename,
        "score": score,
        "skills": skills,
        "word_count": word_count,
    }