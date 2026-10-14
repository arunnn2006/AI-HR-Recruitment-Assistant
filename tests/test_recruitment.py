from copy import deepcopy
import json
from types import SimpleNamespace

import pytest

import openai
from src.agent import RecruitmentAgent, _validate_live_report
from src.repository import RecruitmentRepository
from src.tools import RecruitmentTools


@pytest.fixture
def tools():
    return RecruitmentTools(RecruitmentRepository())


def test_complete_candidate_scores_and_is_shortlisted(tools):
    result = tools.evaluate_candidate("software-engineer", "maya-patel")
    assert result["match_percentage"] == 95.0
    assert result["missing_mandatory_skills"] == []
    assert result["recommendation"] == "Shortlist"


@pytest.mark.parametrize(
    ("job_id", "candidate_id", "score", "recommendation", "missing_skills"),
    [
        ("software-engineer", "samir-khan", 48.5, "Do not shortlist", ["SQL", "Unit Testing"]),
        (
            "software-engineer",
            "jonah-williams",
            44.0,
            "Do not shortlist",
            ["REST APIs", "Git", "Unit Testing"],
        ),
        ("data-engineer", "jonah-williams", 78.0, "Review", ["Apache Airflow"]),
        (
            "backend-engineer",
            "elena-rossi",
            76.0,
            "Review",
            ["PostgreSQL", "Distributed Systems"],
        ),
    ],
)
def test_expected_candidate_scenarios(
    tools, job_id, candidate_id, score, recommendation, missing_skills
):
    result = tools.evaluate_candidate(job_id, candidate_id)

    assert result["match_percentage"] == score
    assert result["recommendation"] == recommendation
    assert result["missing_mandatory_skills"] == missing_skills


def test_missing_mandatory_skill_is_reported(tools):
    result = tools.evaluate_candidate("data-engineer", "jonah-williams")
    assert "Apache Airflow" in result["missing_mandatory_skills"]
    assert result["match_percentage"] < 80


def test_demo_report_is_labeled_and_requires_human_review(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    report = RecruitmentAgent().run(
        "Evaluate Maya Patel", "software-engineer", ["maya-patel"]
    )

    assert report["mode"] == "demo"
    assert report["human_review_required"] is True
    assert len(report["shortlisted_candidates"][0]["interview_questions"]) == 3


def test_empty_recruitment_request_is_rejected():
    with pytest.raises(ValueError, match="Recruitment request cannot be empty"):
        RecruitmentAgent().run("", "software-engineer", ["maya-patel"])


def test_empty_or_duplicate_candidate_selection_is_rejected():
    agent = RecruitmentAgent()

    with pytest.raises(ValueError, match="No candidates are available"):
        agent.run("Review candidates", "software-engineer", [])
    with pytest.raises(ValueError, match="Candidate IDs must be unique"):
        agent.run(
            "Review candidates",
            "software-engineer",
            ["maya-patel", "maya-patel"],
        )


def test_interview_questions_are_exactly_three(tools):
    assert len(tools.generate_interview_questions("backend-engineer", "elena-rossi")) == 3


def test_evaluation_includes_candidate_evidence(tools):
    result = tools.evaluate_candidate("software-engineer", "maya-patel")
    profile = tools.get_candidate_profiles(["maya-patel"])[0]

    assert result["evidence"] == {
        "projects": profile["projects"],
        "education": profile["education"],
        "certifications": profile["certifications"],
    }
    assert result["explanation"]


def _valid_live_report(tools):
    request = "Evaluate Maya Patel for the Software Engineer role."
    job = tools.get_job_description("software-engineer")
    evaluation = tools.evaluate_candidate("software-engineer", "maya-patel")
    questions = tools.generate_interview_questions(
        "software-engineer", "maya-patel"
    )
    report = {
        "mode": "live",
        "request": request,
        "job": job,
        "candidates_evaluated": [evaluation],
        "shortlisted_candidates": [
            {
                "candidate_id": "maya-patel",
                "candidate_name": "Maya Patel",
                "interview_questions": questions,
            }
        ],
        "human_review_required": True,
        "note": "Human review remains required.",
    }
    validated = _validate_live_report(
        report,
        request,
        job,
        [evaluation],
        job,
        {"maya-patel": evaluation},
        {"maya-patel": questions},
    )
    return report, validated, (request, job, evaluation, questions)


def test_live_report_validation_returns_deterministic_scores(tools):
    _, report, (_, _, evaluation, questions) = _valid_live_report(tools)

    assert report["mode"] == "live"
    assert report["human_review_required"] is True
    assert report["candidates_evaluated"] == [evaluation]
    assert report["candidates_evaluated"][0]["match_percentage"] == 95.0
    assert report["shortlisted_candidates"][0]["interview_questions"] == questions


def test_live_agent_uses_tools_and_validates_provider_report(monkeypatch, tools):
    request = "Evaluate Maya Patel for the Software Engineer role."
    job = tools.get_job_description("software-engineer")
    evaluation = tools.evaluate_candidate("software-engineer", "maya-patel")
    questions = tools.generate_interview_questions(
        "software-engineer", "maya-patel"
    )
    final_report = {
        "mode": "live",
        "request": request,
        "job": job,
        "candidates_evaluated": [evaluation],
        "shortlisted_candidates": [
            {
                "candidate_id": "maya-patel",
                "candidate_name": "Maya Patel",
                "interview_questions": questions,
            }
        ],
        "human_review_required": True,
        "note": "Human review remains required.",
    }
    calls = [
        SimpleNamespace(
            id="job-call",
            function=SimpleNamespace(
                name="get_job_description",
                arguments=json.dumps({"job_id": "software-engineer"}),
            ),
        ),
        SimpleNamespace(
            id="evaluation-call",
            function=SimpleNamespace(
                name="evaluate_candidate",
                arguments=json.dumps(
                    {
                        "job_id": "software-engineer",
                        "candidate_id": "maya-patel",
                    }
                ),
            ),
        ),
        SimpleNamespace(
            id="questions-call",
            function=SimpleNamespace(
                name="generate_interview_questions",
                arguments=json.dumps(
                    {
                        "job_id": "software-engineer",
                        "candidate_id": "maya-patel",
                    }
                ),
            ),
        ),
    ]
    messages = [
        SimpleNamespace(
            tool_calls=calls,
            content=None,
            model_dump=lambda **_: {"role": "assistant", "tool_calls": []},
        ),
        SimpleNamespace(
            tool_calls=None,
            content=json.dumps(final_report),
            model_dump=lambda **_: {"role": "assistant", "content": ""},
        ),
    ]

    class FakeClient:
        def __init__(self, **_):
            self.chat = SimpleNamespace(
                completions=SimpleNamespace(
                    create=lambda **_: SimpleNamespace(
                        choices=[SimpleNamespace(message=messages.pop(0))]
                    )
                )
            )

    monkeypatch.setattr(openai, "OpenAI", FakeClient)
    monkeypatch.setenv("OPENAI_API_KEY", "test-only-placeholder")

    report = RecruitmentAgent(tools).run(
        request, "software-engineer", ["maya-patel"]
    )

    assert report["mode"] == "live"
    assert report["human_review_required"] is True
    assert report["candidates_evaluated"][0]["match_percentage"] == 95.0
    assert report["shortlisted_candidates"][0]["interview_questions"] == questions


@pytest.mark.parametrize(
    ("mutation", "error"),
    [
        (lambda report: report.pop("note"), "missing required fields"),
        (
            lambda report: report.update(human_review_required=False),
            "human_review_required to true",
        ),
        (
            lambda report: report["candidates_evaluated"][0].update(
                match_percentage=100.0
            ),
            "does not match deterministic tool output",
        ),
        (
            lambda report: report["shortlisted_candidates"][0].update(
                interview_questions=["Invented question"]
            ),
            "exactly three questions returned by the deterministic tool",
        ),
    ],
)
def test_live_report_validation_rejects_invalid_or_misleading_output(
    tools, mutation, error
):
    report, _, (request, job, evaluation, questions) = _valid_live_report(tools)
    report = deepcopy(report)
    mutation(report)

    with pytest.raises(ValueError, match=error):
        _validate_live_report(
            report,
            request,
            job,
            [evaluation],
            job,
            {"maya-patel": evaluation},
            {"maya-patel": questions},
        )


def test_live_report_validation_requires_successful_tool_calls(tools):
    report, _, (request, job, evaluation, questions) = _valid_live_report(tools)

    with pytest.raises(ValueError, match="Job retrieval tool"):
        _validate_live_report(
            report,
            request,
            job,
            [evaluation],
            None,
            {"maya-patel": evaluation},
            {"maya-patel": questions},
        )
    with pytest.raises(ValueError, match="Deterministic evaluation tool"):
        _validate_live_report(
            report,
            request,
            job,
            [evaluation],
            job,
            {},
            {"maya-patel": questions},
        )
    with pytest.raises(ValueError, match="exactly three questions"):
        _validate_live_report(
            report,
            request,
            job,
            [evaluation],
            job,
            {"maya-patel": evaluation},
            {},
        )


def test_candidate_search_retrieves_relevant_evidence(tools):
    results = tools.search_candidates("Snowflake warehouse")

    assert results
    assert results[0]["id"] == "jonah-williams"
    assert "Snowflake" in " ".join(results[0]["projects"])


def test_invalid_ids_and_empty_search_are_rejected(tools):
    with pytest.raises(ValueError, match="Invalid job ID"):
        tools.get_job_description("missing-job")
    with pytest.raises(ValueError, match="Invalid candidate ID"):
        tools.evaluate_candidate("software-engineer", "missing-candidate")
    with pytest.raises(ValueError, match="cannot be empty"):
        tools.search_candidates(" ")


def test_comparison_is_sorted(tools):
    results = tools.compare_candidates("software-engineer", ["samir-khan", "maya-patel"])
    assert results[0]["candidate_id"] == "maya-patel"
