from .models import CandidateProfile, Evaluation, JobDescription


def _matching(required: list[str], available: list[str]) -> tuple[list[str], list[str]]:
    available_lower = {item.lower(): item for item in available}
    matched = [item for item in required if item.lower() in available_lower]
    missing = [item for item in required if item.lower() not in available_lower]
    return matched, missing


def evaluate_candidate(job: JobDescription, candidate: CandidateProfile) -> Evaluation:
    matched_mandatory, missing_mandatory = _matching(job.mandatory_skills, candidate.skills)
    matched_preferred, _ = _matching(job.preferred_skills, candidate.skills)
    mandatory_score = len(matched_mandatory) / len(job.mandatory_skills) * 60
    preferred_score = len(matched_preferred) / len(job.preferred_skills) * 20
    experience_score = min(candidate.years_experience / job.minimum_years_experience, 1.0) * 15
    education_score = 5 if any(target.lower() in education.lower() for target in job.education for education in candidate.education) else 0
    score = round(mandatory_score + preferred_score + experience_score + education_score, 1)
    experience_summary = f"{candidate.years_experience:g} years; role minimum is {job.minimum_years_experience} years"
    recommendation = "Shortlist" if not missing_mandatory and score >= 70 else "Review" if score >= 50 else "Do not shortlist"
    explanation = (f"Matched {len(matched_mandatory)}/{len(job.mandatory_skills)} mandatory skills and "
                   f"{len(matched_preferred)}/{len(job.preferred_skills)} preferred skills. "
                   f"Experience: {experience_summary}. Evidence includes {len(candidate.projects)} relevant project(s).")
    return Evaluation(
        candidate_id=candidate.id,
        candidate_name=candidate.name,
        matched_mandatory_skills=matched_mandatory,
        missing_mandatory_skills=missing_mandatory,
        matched_preferred_skills=matched_preferred,
        experience_summary=experience_summary,
        score=score,
        explanation=explanation,
        recommendation=recommendation,
        evidence={"projects": candidate.projects, "education": candidate.education, "certifications": candidate.certifications},
    )
