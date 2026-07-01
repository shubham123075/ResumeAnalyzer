import re


SKILLS_DB = [
    "python", "java", "c++", "machine learning", "data science", "sql",
    "html", "css", "javascript", "flask", "django", "react", "node",
    "excel", "power bi", "tableau", "git", "api", "aws", "azure",
    "communication", "leadership", "problem solving"
]

ACTION_VERBS = [
    "built", "developed", "created", "implemented", "designed", "managed",
    "led", "optimized", "improved", "delivered", "analyzed", "automated"
]

SECTION_KEYWORDS = {
    "experience": ["experience", "employment", "work history", "internship"],
    "projects": ["project", "projects"],
    "education": ["education", "degree", "university", "college"],
    "skills": ["skills", "technical skills", "technologies"],
    "achievements": ["achievement", "achievements", "awards", "certification", "certifications"],
}


def clean_text(text):
    return re.sub(r"\s+", " ", text or "").strip()


def extract_skills(text):
    lowered = text.lower()
    found_skills = [skill for skill in SKILLS_DB if skill in lowered]
    return sorted(set(found_skills))


def has_any(text, keywords):
    lowered = text.lower()
    return any(keyword in lowered for keyword in keywords)


def count_numbers(text):
    return len(re.findall(r"\b\d+%?|\b\d+\+\b", text))


def detect_sections(text):
    return {
        section: has_any(text, keywords)
        for section, keywords in SECTION_KEYWORDS.items()
    }


def get_candidate_name(text):
    for line in text.splitlines():
        cleaned = line.strip()
        if 2 <= len(cleaned) <= 60 and not any(char.isdigit() for char in cleaned):
            if "resume" not in cleaned.lower() and "curriculum" not in cleaned.lower():
                return cleaned
    return "This candidate"


def generate_summary(text, skills, sections, score):
    name = get_candidate_name(text)
    skill_phrase = ", ".join(skills[:6]) if skills else "a clearer technical skill set"

    if score >= 80:
        position = "presents a strong and recruiter-friendly profile"
    elif score >= 65:
        position = "has a promising profile that can become stronger with sharper evidence"
    else:
        position = "needs a clearer structure, stronger keywords, and more measurable proof"

    experience_note = (
        "The resume shows work or internship experience, which helps establish practical credibility."
        if sections["experience"]
        else "Adding internships, projects, freelance work, or practical experience would make the profile more convincing."
    )

    return (
        f"{name} {position}. The document currently highlights {skill_phrase}, "
        f"with an ATS readiness score of {score}/100. {experience_note} "
        "For a more competitive application, the resume should connect skills to specific outcomes, "
        "add measurable achievements where possible, and keep the strongest keywords visible in the top half of the document."
    )


def analyze_resume(text):
    text = text or ""
    cleaned = clean_text(text)
    lowered = cleaned.lower()
    skills = extract_skills(cleaned)
    sections = detect_sections(cleaned)
    number_count = count_numbers(cleaned)
    action_verb_count = sum(1 for verb in ACTION_VERBS if verb in lowered)

    strengths = []
    weaknesses = []
    suggestions = []

    if len(skills) >= 6:
        strengths.append("Strong keyword coverage across technical or professional skills.")
    elif skills:
        strengths.append("Some relevant skills are visible, giving the resume a useful starting point.")
        weaknesses.append("Skill coverage is still limited for ATS keyword matching.")
        suggestions.append("Add a dedicated skills section with role-specific tools, technologies, and soft skills.")
    else:
        weaknesses.append("No major skills were detected clearly by the analyzer.")
        suggestions.append("Add a clearly labeled skills section near the top of the resume.")

    if sections["experience"]:
        strengths.append("Experience or internship information is present.")
    else:
        weaknesses.append("Experience is not clearly visible.")
        suggestions.append("Add internships, freelance work, volunteering, or project-based experience.")

    if sections["projects"]:
        strengths.append("Project information helps demonstrate practical ability.")
    else:
        suggestions.append("Add 2-3 strong projects with tools used, problem solved, and final outcome.")

    if number_count >= 3:
        strengths.append("The resume includes measurable details, which improves recruiter confidence.")
    else:
        weaknesses.append("The resume needs more numbers, metrics, or measurable achievements.")
        suggestions.append("Use numbers such as percentages, team size, project duration, users, revenue, or performance gains.")

    if action_verb_count >= 4:
        strengths.append("Action-oriented language makes the profile sound more active and professional.")
    else:
        suggestions.append("Start bullet points with stronger action verbs like built, improved, managed, automated, or delivered.")

    missing_sections = [name.title() for name, present in sections.items() if not present]
    if missing_sections:
        weaknesses.append("Missing or unclear sections: " + ", ".join(missing_sections[:4]) + ".")

    score = 45
    score += min(len(skills) * 5, 30)
    score += 8 if sections["experience"] else 0
    score += 7 if sections["projects"] else 0
    score += 5 if sections["education"] else 0
    score += min(number_count * 2, 10)
    score += min(action_verb_count, 5)
    score = min(score, 100)

    summary = generate_summary(cleaned, skills, sections, score)

    if score >= 80:
        verdict = "High potential"
    elif score >= 65:
        verdict = "Good foundation"
    else:
        verdict = "Needs improvement"

    focus_areas = []
    if len(skills) < 6:
        focus_areas.append("Keyword depth")
    if number_count < 3:
        focus_areas.append("Measurable achievements")
    if not sections["projects"]:
        focus_areas.append("Project proof")
    if not sections["experience"]:
        focus_areas.append("Experience clarity")
    if not focus_areas:
        focus_areas.append("Final polish and role-specific tailoring")

    return {
        "summary": summary,
        "skills": skills,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "suggestions": suggestions,
        "score": score,
        "verdict": verdict,
        "focus_areas": focus_areas,
        "sections": sections,
        "metrics_found": number_count,
        "action_verbs_found": action_verb_count,
    }
