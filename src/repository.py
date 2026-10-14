import json
from pathlib import Path
from typing import Any

from .models import CandidateProfile, JobDescription


class RecruitmentRepository:
    def __init__(self, data_dir: str | Path | None = None) -> None:
        self.data_dir = Path(data_dir or Path(__file__).resolve().parents[1] / "data")

    def _load(self, filename: str) -> list[dict[str, Any]]:
        path = self.data_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Recruitment data unavailable: {path}")
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            raise ValueError(f"Malformed recruitment data: {filename}") from exc

    def get_jobs(self) -> list[JobDescription]:
        return [JobDescription(**item) for item in self._load("jobs.json")]

    def get_candidates(self) -> list[CandidateProfile]:
        return [CandidateProfile(**item) for item in self._load("candidates.json")]

    def get_job(self, job_id: str) -> JobDescription:
        for job in self.get_jobs():
            if job.id == job_id:
                return job
        raise ValueError(f"Invalid job ID: {job_id}")

    def get_candidate(self, candidate_id: str) -> CandidateProfile:
        for candidate in self.get_candidates():
            if candidate.id == candidate_id:
                return candidate
        raise ValueError(f"Invalid candidate ID: {candidate_id}")
