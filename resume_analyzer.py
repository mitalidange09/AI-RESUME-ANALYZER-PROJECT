import re
from collections import Counter

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

try:
    stopwords.words('english')
except LookupError:
    nltk.download('stopwords', quiet=True)
    nltk.download('punkt', quiet=True)

TECHNICAL_SKILLS = [
    'Python', 'Java', 'C', 'C++', 'SQL', 'MySQL', 'HTML', 'CSS', 'JavaScript', 'Flask', 'Django',
    'React', 'Machine Learning', 'Artificial Intelligence', 'NLP', 'Pandas', 'NumPy', 'Scikit-learn',
    'TensorFlow', 'Git', 'GitHub', 'Data Analysis', 'Power BI', 'Excel'
]

SOFT_SKILLS = [
    'Communication', 'Teamwork', 'Leadership', 'Problem Solving', 'Time Management', 'Creativity'
]

COMMON_KEYWORDS = {
    'education': ['bcs', 'bca', 'b.tech', 'be', 'mca', 'msc', 'mba', 'bachelor', 'master', 'diploma'],
    'experience': ['internship', 'work experience', 'experience', 'fresher', 'developer', 'analyst', 'engineer'],
}


def clean_text(text):
    if not text:
        return ''
    text = text.lower()
    text = re.sub(r'[^a-z0-9+\-\s.,]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def tokenize_text(text):
    cleaned = clean_text(text)
    tokens = word_tokenize(cleaned, preserve_line=True)
    stop = set(stopwords.words('english'))
    return [token for token in tokens if token and token not in stop and len(token) > 2]


def extract_resume_skills(resume_text):
    text = (resume_text or '').lower()
    technical_found = []
    soft_found = []

    for skill in TECHNICAL_SKILLS:
        skill_lower = skill.lower()
        if skill_lower in text:
            technical_found.append(skill)

    for skill in SOFT_SKILLS:
        skill_lower = skill.lower()
        if skill_lower in text:
            soft_found.append(skill)

    return {
        'technical': technical_found,
        'soft': soft_found,
    }


def extract_education(resume_text):
    text = (resume_text or '').lower()
    education_keywords = [
        'bcs', 'bca', 'b.tech', 'be', 'mca', 'msc', 'mba', 'bachelor', 'master', 'diploma'
    ]
    for keyword in education_keywords:
        if keyword in text:
            return keyword.upper() if keyword.isalpha() else keyword.upper()
    return 'Not detected'


def extract_experience(resume_text):
    text = (resume_text or '').lower()
    if re.search(r'\b(fresher|fresh graduate|new graduate)\b', text):
        return 'Fresher / Not detected'
    if re.search(r'\b(internship|intern|experience|work experience)\b', text):
        matched = re.findall(r'(?:\d+\s*[-+to]{1,2}\s*\d+\s*years|\d+\s*years|\d+\s*months)', text)
        if matched:
            return matched[0]
        return 'Experience detected'
    return 'Fresher / Not detected'


def extract_keywords(resume_text, top_n=15):
    tokens = tokenize_text(resume_text)
    counts = Counter(tokens)
    common_exclusions = {
        'resume', 'skills', 'experience', 'education', 'python', 'using', 'work', 'project', 'projects',
        'communication', 'teamwork', 'leader', 'management', 'analysis', 'data', 'developer', 'job'
    }
    keywords = [word for word, _ in counts.most_common(top_n) if word not in common_exclusions]
    return keywords


def calculate_resume_score(resume_text, education, experience, all_skills, keywords):
    text = resume_text or ''
    criteria = {
        'name': bool(re.search(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b', text)),
        'email': bool(re.search(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', text)),
        'phone': bool(re.search(r'(?:\+?\d[\d\s().-]{7,}\d)', text)),
        'education': education != 'Not detected',
        'skills': len(all_skills) > 0,
        'experience': experience != 'Fresher / Not detected',
        'projects': bool(re.search(r'\b(project|projects|portfolio|achievement|workshop)\b', text, re.I)),
        'certifications': bool(re.search(r'\b(certification|certified|aws|azure|oracle|google)\b', text, re.I)),
        'keywords': bool(keywords)
    }

    total = len(criteria)
    passed = sum(1 for value in criteria.values() if value)
    score = round((passed / total) * 100, 2)
    return {
        'score': score,
        'criteria': criteria,
    }
