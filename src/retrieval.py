import re
from dataclasses import asdict

from .models import CandidateProfile
from .repository import RecruitmentRepository


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9+#.]+", text.lower()))


class RecruitmentRetriever:
    """Small transparent lexical retriever for local recruitment knowledge."""

    def __init__(self, repository: RecruitmentRepository) -> None:
        self.repository = repository

    def search_jobs(self, query: str, limit: int = 3) -> list[dict]:
        query_tokens = _tokens(query)
        ranked = []
        for job in self.repository.get_jobs():
            text = " ".join([job.title, job.summary, *job.mandatory_skills, *job.preferred_skills])
            score = len(query_tokens & _tokens(text))
            ranked.append((score, job))
        return [asdict(job) for score, job in sorted(ranked, key=lambda item: item[0], reverse=True)[:limit] if score > 0]

    def search_candidates(self, query: str, job_id: str | None = None, limit: int = 5) -> list[dict]:
        query_tokens = _tokens(query)
        job = self.repository.get_job(job_id) if job_id else None
        ranked: list[tuple[int, CandidateProfile]] = []
        for candidate in self.repository.get_candidates():
            text = " ".join([candidate.name, candidate.headline, *candidate.skills, *candidate.projects, *candidate.strengths])
            score = len(query_tokens & _tokens(text))
            if job:
                score += len(set(map(str.lower, candidate.skills)) & set(map(str.lower, job.mandatory_skills))) * 2
            ranked.append((score, candidate))
        ranked.sort(key=lambda item: item[0], reverse=True)
        return [asdict(candidate) for score, candidate in ranked[:limit] if score > 0 or not query.strip()]
