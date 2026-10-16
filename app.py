import logging
import os

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from config import Config
from database import create_database
from job_recommender import recommend_jobs
from models import User, Resume, Job, db

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

print(
    f"[DB config] host={Config.DB_HOST} user={Config.DB_USER} "
    f"database={Config.DB_NAME} password_set={bool(Config.DB_PASSWORD)}"
)

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)


db.init_app(app)

try:
    create_database()
except Exception as exc:  # pragma: no cover - startup safety guard
    logger.warning("Database initialization skipped during startup: %s", exc)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def _analyze_resume_record(resume):
    from resume_analyzer import (
        calculate_resume_score,
        extract_education,
        extract_experience,
        extract_keywords,
        extract_resume_skills,
    )
    from resume_parser import extract_resume_text

    resume_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        os.path.basename(resume.resume_file),
    )
    resume_text = extract_resume_text(resume_path) or resume.resume_text or ""
    skills = extract_resume_skills(resume_text)
    all_skills = skills["technical"] + skills["soft"]
    education = extract_education(resume_text)
    experience = extract_experience(resume_text)
    keywords = extract_keywords(resume_text)
    analysis = calculate_resume_score(
        resume_text,
        education,
        experience,
        all_skills,
        keywords,
    )
    return {
        "text": resume_text,
        "skills": skills,
        "education": education,
        "experience": experience,
        "keywords": keywords,
        "analysis": analysis,
    }


def _recommendations_for_resume(resume, profile=None):
    profile = profile or _analyze_resume_record(resume)
    return recommend_jobs(
        Job.query.order_by(Job.job_id).all(),
        profile["text"],
        profile["skills"],
        education=profile["education"],
        experience=profile["experience"],
        keywords=profile["keywords"],
        limit=8,
    )


@app.route("/")
def index():
    if current_user.is_authenticated:
        if current_user.role == "admin":
            return redirect(url_for("admin_dashboard"))
        return redirect(url_for("dashboard"))
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        phone = request.form.get("phone", "").strip()

        if not name or not email or not password:
            flash("Name, email, and password are required.", "danger")
            return render_template("register.html")

        if User.query.filter_by(email=email).first():
            flash("An account with that email already exists.", "warning")
            return render_template("register.html")

        user = User(
            name=name,
            email=email,
            password=generate_password_hash(password),
            phone=phone or None,
            role="candidate",
        )
        db.session.add(user)
        db.session.commit()

        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            if user.role == "admin":
                return redirect(url_for("admin_dashboard"))
            return redirect(url_for("dashboard"))

        flash("Invalid email or password.", "danger")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required
def dashboard():
    resumes = Resume.query.filter_by(user_id=current_user.user_id).order_by(Resume.upload_date.desc()).all()
    skill_count = 0
    for resume in resumes:
        skill_count += len(set((resume.resume_text or "").lower().split()))

    return render_template(
        "dashboard.html",
        user=current_user,
        resumes=resumes,
        total_resumes=len(resumes),
        latest_resume=resumes[0] if resumes else None,
        skill_count=skill_count,
        recommended_count=min(Job.query.count(), 8) if resumes else 0,
    )


@app.route("/resume-analysis/<int:resume_id>")
@login_required
def resume_analysis(resume_id):
    resume = Resume.query.filter_by(
        resume_id=resume_id,
        user_id=current_user.user_id,
    ).first_or_404()

    profile = _analyze_resume_record(resume)
    recommendations = _recommendations_for_resume(resume, profile)

    return render_template(
        "resume_analysis.html",
        resume=resume,
        analysis={
            **profile["analysis"],
            "education": profile["education"],
            "experience": profile["experience"],
            "keywords": profile["keywords"],
        },
        technical_skills=profile["skills"]["technical"],
        soft_skills=profile["skills"]["soft"],
        recommendations=recommendations,
    )


@app.route("/upload_resume", methods=["GET", "POST"])
@login_required
def upload_resume():
    if request.method == "POST":
        if "resume" not in request.files:
            flash("Resume file not found.", "danger")
            return render_template("upload_resume.html")

        file = request.files["resume"]
        if file.filename == "":
            flash("Please select a resume file.", "warning")
            return render_template("upload_resume.html")

        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in {".pdf", ".docx"}:
            flash("Only PDF and DOCX files are allowed.", "danger")
            return render_template("upload_resume.html")

        safe_name = os.path.basename(file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], safe_name)
        file.save(file_path)

        resume = Resume(
            user_id=current_user.user_id,
            resume_file=safe_name,
            resume_text="Upload processed successfully.",
        )
        db.session.add(resume)
        db.session.commit()
        flash("Resume uploaded successfully.", "success")
        return redirect(url_for("dashboard"))

    return render_template("upload_resume.html")


@app.route("/jobs")
@login_required
def jobs():
    all_jobs = Job.query.order_by(Job.job_title).all()
    return render_template("jobs.html", jobs=all_jobs)


@app.route("/recommended_jobs")
@login_required
def recommended_jobs():
    sort_by = request.args.get("sort", "highest")
    resume_id = request.args.get("resume_id", type=int)
    if resume_id is not None:
        resume = Resume.query.filter_by(
            resume_id=resume_id,
            user_id=current_user.user_id,
        ).first_or_404()
    else:
        resume = Resume.query.filter_by(
            user_id=current_user.user_id,
        ).order_by(Resume.upload_date.desc()).first()
    recommendations = _recommendations_for_resume(resume) if resume else []

    if sort_by == "lowest":
        recommendations.sort(key=lambda item: item["match_score"])
    elif sort_by == "title":
        recommendations.sort(key=lambda item: item["job"].job_title.lower())

    return render_template(
        "recommended_jobs.html",
        recommendations=recommendations,
        sort_by=sort_by,
        resume=resume,
        recommendation_count=len(recommendations),
    )


@app.route("/profile")
@login_required
def profile():
    resumes = Resume.query.filter_by(user_id=current_user.user_id).order_by(Resume.upload_date.desc()).all()
    return render_template("profile.html", user=current_user, resumes=resumes)


@app.route("/job/<int:job_id>")
@login_required
def job_details(job_id):
    job = Job.query.get_or_404(job_id)
    return render_template("job_details.html", job=job, match_score=None, matched_skills=[], missing_skills=[])


@app.route("/admin")
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        flash("Admin access required.", "danger")
        return redirect(url_for("dashboard"))
    return render_template("admin/dashboard.html")


@app.route("/admin/users")
@login_required
def admin_users():
    if current_user.role != "admin":
        flash("Admin access required.", "danger")
        return redirect(url_for("dashboard"))
    return render_template("admin/users.html", users=User.query.order_by(User.created_at.desc()).all())


@app.route("/admin/jobs")
@login_required
def admin_jobs():
    if current_user.role != "admin":
        flash("Admin access required.", "danger")
        return redirect(url_for("dashboard"))
    return render_template("admin/jobs.html", jobs=Job.query.order_by(Job.created_at.desc()).all())


@app.route("/admin/analyses")
@login_required
def admin_analyses():
    if current_user.role != "admin":
        flash("Admin access required.", "danger")
        return redirect(url_for("dashboard"))
    return render_template("admin/analyses.html", resumes=Resume.query.order_by(Resume.upload_date.desc()).all())


if __name__ == "__main__":
    app.run(debug=True, port=8000)