from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class JobDescription:
    id: str
    title: str
    department: str
    location: str
    summary: str
    mandatory_skills: list[str]
    preferred_skills: list[str]
    minimum_years_experience: int
    education: list[str]
    responsibilities: list[str]


@dataclass(frozen=True)
class CandidateProfile:
    id: str
    name: str
    headline: str
    skills: list[str]
    years_experience: float
    education: list[str]
    projects: list[str]
    certifications: list[str]
    strengths: list[str]
    missing_skills: list[str]


@dataclass
class Evaluation:
    candidate_id: str
    candidate_name: str
    matched_mandatory_skills: list[str]
    missing_mandatory_skills: list[str]
    matched_preferred_skills: list[str]
    experience_summary: str
    score: float
    explanation: str
    recommendation: str
    evidence: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "candidate_name": self.candidate_name,
            "matched_mandatory_skills": self.matched_mandatory_skills,
            "missing_mandatory_skills": self.missing_mandatory_skills,
            "matched_preferred_skills": self.matched_preferred_skills,
            "experience_summary": self.experience_summary,
            "match_percentage": self.score,
            "explanation": self.explanation,
            "recommendation": self.recommendation,
            "evidence": self.evidence,
        }
