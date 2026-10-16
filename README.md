# AI Resume Analyzer and Job Recommendation System

This project is a complete Flask-based resume analysis and job recommendation system for local Windows VS Code development. It allows a candidate to register, upload a PDF or DOCX resume, analyze extracted skills and education, and view recommended jobs based on job skill matching.

## Problem
Candidates do not always know whether their resume matches job requirements.

## Purpose
Use AI/NLP to analyze resumes and recommend suitable jobs based on matching skills and available job data.

## Main Modules
- User Registration/Login
- Resume Upload
- Resume Parsing
- Resume Analysis
- Job Management
- Resume-Job Matching
- Job Recommendation
- Admin

## Project Structure

```text
AI-Resume-Job-Recommender/
├── app.py
├── config.py
├── database.py
├── models.py
├── resume_parser.py
├── resume_analyzer.py
├── job_recommender.py
├── requirements.txt
├── README.md
├── .env
├── create_admin.py
├── uploads/
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── script.js
│   └── images/
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── upload_resume.html
│   ├── resume_analysis.html
│   ├── recommended_jobs.html
│   ├── jobs.html
│   ├── job_details.html
│   ├── profile.html
│   ├── admin/
│   │   ├── dashboard.html
│   │   ├── users.html
│   │   ├── jobs.html
│   │   ├── add_job.html
│   │   ├── edit_job.html
│   │   └── analyses.html
├── sql/
│   └── database.sql
└── .env
```

## Installation Steps for Windows VS Code

### Step 1: Install Python
1. Download Python from https://www.python.org/downloads/windows/
2. During installation, check "Add Python to PATH".
3. Verify:

```bash
python --version
```

### Step 2: Install MySQL
1. Download and install MySQL Community Server.
2. Make sure MySQL Server is running.
3. Use MySQL Workbench or command line to create the database.

### Step 3: Create the Project Folder
Create a folder named `AI-Resume-Job-Recommender` in your preferred location.

### Step 4: Open the Folder in VS Code
Open the project directory in Visual Studio Code.

### Step 5: Create Virtual Environment
In the terminal, run:

```bash
python -m venv venv
```

### Step 6: Activate the Virtual Environment
Run:

```bash
venv\Scripts\activate
```

### Step 7: Install Dependencies
Run:

```bash
pip install -r requirements.txt
```

### Step 8: Create MySQL Database
Open MySQL and run:

```sql
CREATE DATABASE ai_resume_recommender;
```

### Step 9: Run SQL Script
From the project folder, run:

```bash
mysql -u root -p < sql\database.sql
```

If using MySQL Workbench, open the file and run the script manually.

### Step 10: Configure .env
Create or edit the `.env` file in the project root and change only the password value:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=YOUR_MYSQL_PASSWORD
DB_NAME=ai_resume_recommender
SECRET_KEY=change-this-secret-key
```

Important: replace `YOUR_MYSQL_PASSWORD` with the password you set for your local MySQL root account. If you use a different MySQL user, update `DB_USER` and `DB_PASSWORD` accordingly.

### Step 11: Run the Application

```bash
python app.py
```

### Step 12: Open in Browser
Visit:

```text
http://127.0.0.1:8000
```

## Create the First Admin Account
The project includes a helper file named `create_admin.py`.

Run:

```bash
python create_admin.py
```

This creates a sample admin account:

```text
Email: admin@example.com
Password: admin123
```

Important: change the password before using this for anything serious. This is only for local academic testing.

## Matching Formula
The recommender scores every available job for the selected resume, normalizes common skill aliases, then returns the best eight without a minimum-score cutoff. The overall ranking combines:

```text
Overall Match = 70% skill overlap + 20% job-title overlap + 10% profile-keyword overlap
```

The skill component is `(matched required skills / distinct required skills) × 100`. Empty skill fields are handled safely; title and description terms can still contribute to the score. `ML`/`machine learning`, `AI`/`artificial intelligence`, `JS`/`JavaScript`, and `MySQL`/`SQL` are normalized for matching.

On startup, if the MySQL `jobs` table contains fewer than eight records, the application adds missing entries from a built-in set of 15 sample jobs. Seeding compares job title and company, so restarting the application does not repeatedly insert those sample records. You can add other jobs through an SQL client by inserting a row into `jobs` with `job_title`, `company_name`, `location`, `description`, `required_skills`, `experience`, and optional `salary`.

## How to Test the App

### Candidate Testing Steps
1. Open the app in the browser.
2. Register a new candidate account.
3. Log in.
4. Go to Dashboard.
5. Upload a PDF or DOCX resume.
6. Review the Resume Analysis page.
7. View Recommended Jobs.
8. Open a job to see match details.

### Admin Testing Steps
1. Log in with the admin account.
2. Open Admin Dashboard.
3. Add, edit, and delete jobs.
4. View users and analysis records.

## Common Errors and Exact Fixes

### 1. No database or database not found
Fix:
```sql
CREATE DATABASE ai_resume_recommender;
```
Then ensure `.env` is configured correctly.

### 2. Table doesn't exist
Fix:
```bash
mysql -u root -p < sql\database.sql
```

### 3. MySQL connection error
Fix:
- Start MySQL Server.
- Confirm `DB_HOST`, `DB_USER`, `DB_PASSWORD`, and `DB_NAME` in `.env`.
- Check that the MySQL user has access to the database.

### 4. Unsupported file type
Fix:
- Upload only `.pdf` or `.docx` files.
- Ensure the file extension is valid.

### 5. Invalid upload or extraction failed
Fix:
- Use a readable resume file.
- Ensure the document is not corrupted.
- Confirm the file is not empty.

### 6. Admin login fails
Fix:
```bash
python create_admin.py
```
Then login with the created admin account.

### 7. Flask import errors
Fix:
```bash
pip install -r requirements.txt
```

### 8. `ModuleNotFoundError: nltk` or similar
Fix:
```bash
pip install -r requirements.txt
```

## Notes
- Recommendations are based on locally available job data and resume skill matching.
- The project is designed as an academic final-year system and should be used for learning and demonstration.
- Do not claim guaranteed job suitability or perfect AI prediction accuracy.

## License
Academic project use only.
