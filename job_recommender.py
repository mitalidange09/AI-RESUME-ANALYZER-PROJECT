import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


SKILL_ALIASES = {
    "ai": "artificial intelligence",
    "js": "javascript",
    "ml": "machine learning",
    "mysql": "sql",
    "py": "python",
}

SKILL_SPLIT_PATTERN = re.compile(r"[,;|/\n]+")
TOKEN_PATTERN = re.compile(r"[a-z0-9+#.]+")


def parse_skill_string(skill_text):
    if not skill_text:
        return []
    if isinstance(skill_text, str):
        items = SKILL_SPLIT_PATTERN.split(skill_text)
    elif isinstance(skill_text, dict):
        items = [item for values in skill_text.values() for item in parse_skill_string(values)]
    else:
        try:
            items = [item for value in skill_text for item in parse_skill_string(value)]
        except TypeError:
            items = [skill_text]
    return [str(item).strip() for item in items if str(item).strip()]


def _normalize_skill(skill):
    normalized = " ".join(str(skill or "").strip().lower().split())
    return SKILL_ALIASES.get(normalized, normalized)


def _tokens(text):
    return set(TOKEN_PATTERN.findall(str(text or "").lower()))


def _overlap_score(target_tokens, profile_tokens):
    if not target_tokens:
        return 0.0
    return len(target_tokens & profile_tokens) / len(target_tokens) * 100


def calculate_skill_match(resume_skills, job_required_skills):
    resume_items = parse_skill_string(resume_skills)
    required_items = parse_skill_string(job_required_skills)
    resume_set = {_normalize_skill(skill) for skill in resume_items}
    job_set = {_normalize_skill(skill) for skill in required_items}
    job_set.discard("")

    matched = [skill for skill in required_items if _normalize_skill(skill) in resume_set]
    matched_normalized = {_normalize_skill(skill) for skill in matched}
    missing = [skill for skill in required_items if _normalize_skill(skill) not in matched_normalized]
    if not job_set:
        score = 0.0
    else:
        score = round(len(resume_set & job_set) / len(job_set) * 100, 2)

    return {
        "match_score": score,
        "matched_skills": list(dict.fromkeys(matched)),
        "missing_skills": list(dict.fromkeys(missing)),
        "job_skill_count": len(job_set),
    }


def calculate_tfidf_similarity(resume_text, job_description):
    if not resume_text or not job_description:
        return 0.0

    vectorizer = TfidfVectorizer(stop_words="english")
    try:
        matrix = vectorizer.fit_transform([resume_text, job_description])
    except ValueError:
        return 0.0
    similarity = cosine_similarity(matrix[0], matrix[1])[0][0]
    return round(float(similarity) * 100, 2)


def build_recommendation_payload(
    resume_text,
    resume_skills,
    job,
    education=None,
    experience=None,
    keywords=None,
):
    required_skills = parse_skill_string(getattr(job, "required_skills", None))
    match = calculate_skill_match(resume_skills, required_skills)
    profile_text = " ".join(
        [
            str(resume_text or ""),
            " ".join(parse_skill_string(resume_skills)),
            str(education or ""),
            str(experience or ""),
            " ".join(parse_skill_string(keywords)),
        ]
    )
    profile_tokens = _tokens(profile_text)
    title_score = _overlap_score(_tokens(getattr(job, "job_title", "")), profile_tokens)
    description_score = _overlap_score(
        _tokens(
            " ".join(
                [
                    getattr(job, "description", "") or "",
                    " ".join(required_skills),
                ]
            )
        ),
        profile_tokens,
    )
    overall_score = round(
        match["match_score"] * 0.7
        + title_score * 0.2
        + description_score * 0.1,
        2,
    )

    return {
        "job": job,
        "match_score": overall_score,
        "skill_score": match["match_score"],
        "matched_skills": match["matched_skills"],
        "missing_skills": match["missing_skills"],
        "required_skills": required_skills,
        "title_score": round(title_score, 2),
        "keyword_score": round(description_score, 2),
        "tfidf_similarity": calculate_tfidf_similarity(
            profile_text,
            getattr(job, "description", "") or "",
        ),
    }


def recommend_jobs(
    jobs,
    resume_text,
    resume_skills,
    education=None,
    experience=None,
    keywords=None,
    limit=8,
):
    if limit <= 0:
        return []

    recommendations = [
        build_recommendation_payload(
            resume_text,
            resume_skills,
            job,
            education=education,
            experience=experience,
            keywords=keywords,
        )
        for job in jobs
    ]
    recommendations.sort(
        key=lambda item: (
            -item["match_score"],
            (getattr(item["job"], "job_title", "") or "").casefold(),
            getattr(item["job"], "job_id", 0) or 0,
        )
    )
    return recommendations[:limit]
