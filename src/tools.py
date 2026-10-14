from dataclasses import asdict
from typing import Any

from .repository import RecruitmentRepository
from .retrieval import RecruitmentRetriever
from .scoring import evaluate_candidate as score_candidate


class RecruitmentTools:
    def __init__(self, repository: RecruitmentRepository | None = None) -> None:
        self.repository = repository or RecruitmentRepository()
        self.retriever = RecruitmentRetriever(self.repository)

    def get_job_description(self, job_id: str) -> dict[str, Any]:
        return asdict(self.repository.get_job(job_id))

    def get_candidate_profiles(self, candidate_ids: list[str] | None = None) -> list[dict[str, Any]]:
        candidates = self.repository.get_candidates()
        if candidate_ids:
            candidates = [self.repository.get_candidate(candidate_id) for candidate_id in candidate_ids]
        return [asdict(candidate) for candidate in candidates]

    def search_candidates(self, query: str, job_id: str | None = None, limit: int = 5) -> list[dict[str, Any]]:
        if not query.strip():
            raise ValueError("Candidate search query cannot be empty")
        return self.retriever.search_candidates(query, job_id, limit)

    def evaluate_candidate(self, job_id: str, candidate_id: str) -> dict[str, Any]:
        job = self.repository.get_job(job_id)
        candidate = self.repository.get_candidate(candidate_id)
        return score_candidate(job, candidate).to_dict()

    def compare_candidates(self, job_id: str, candidate_ids: list[str]) -> list[dict[str, Any]]:
        if len(candidate_ids) < 2:
            raise ValueError("At least two candidate IDs are required for comparison")
        return sorted((self.evaluate_candidate(job_id, candidate_id) for candidate_id in candidate_ids), key=lambda item: item["match_percentage"], reverse=True)

    def generate_interview_questions(self, job_id: str, candidate_id: str) -> list[str]:
        evaluation = self.evaluate_candidate(job_id, candidate_id)
        missing = ", ".join(evaluation["missing_mandatory_skills"]) or "the candidate's strongest technical area"
        matched = ", ".join(evaluation["matched_mandatory_skills"][:2]) or "the role's core systems"
        return [
            f"How would you design and test a production feature using {matched}?",
            f"Walk through a project where you applied {matched}, including trade-offs and measurable evidence.",
            f"How would you close the current gap in {missing} while protecting reliability and delivery speed?",
        ]
