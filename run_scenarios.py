import json
from src.agent import RecruitmentAgent


SCENARIOS = [
    ("Software Engineer recruitment", "software-engineer", ["maya-patel", "samir-khan"]),
    ("Data Engineer recruitment", "data-engineer", ["jonah-williams", "maya-patel"]),
    ("Backend Engineer recruitment", "backend-engineer", ["elena-rossi", "maya-patel"]),
    ("Candidate comparison", "software-engineer", ["maya-patel", "samir-khan"]),
    ("Candidate with missing mandatory skills", "data-engineer", ["jonah-williams"]),
]

for title, job_id, candidate_ids in SCENARIOS:
    print(f"\n## {title}")
    print(json.dumps(RecruitmentAgent().run(title, job_id, candidate_ids), indent=2))

print("\n## Invalid input/error case")
try:
    RecruitmentAgent().run("", "software-engineer", ["maya-patel"])
except ValueError as exc:
    print(json.dumps({"error": f"{type(exc).__name__}: {exc}"}))
