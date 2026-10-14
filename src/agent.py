import json
import logging
import os
from typing import Any

from dotenv import load_dotenv

from .tools import RecruitmentTools

load_dotenv()
logger = logging.getLogger(__name__)

TOOL_SCHEMAS = [
    {"type": "function", "function": {"name": "get_job_description", "description": "Retrieve one job description by ID.", "parameters": {"type": "object", "properties": {"job_id": {"type": "string"}}, "required": ["job_id"]}}},
    {"type": "function", "function": {"name": "get_candidate_profiles", "description": "Retrieve candidate profiles, optionally by IDs.", "parameters": {"type": "object", "properties": {"candidate_ids": {"type": "array", "items": {"type": "string"}}}}}},
    {"type": "function", "function": {"name": "search_candidates", "description": "Retrieve candidates relevant to a job and natural-language query.", "parameters": {"type": "object", "properties": {"query": {"type": "string"}, "job_id": {"type": "string"}, "limit": {"type": "integer"}}, "required": ["query"]}}},
    {"type": "function", "function": {"name": "evaluate_candidate", "description": "Calculate an evidence-based deterministic candidate evaluation.", "parameters": {"type": "object", "properties": {"job_id": {"type": "string"}, "candidate_id": {"type": "string"}}, "required": ["job_id", "candidate_id"]}}},
    {"type": "function", "function": {"name": "compare_candidates", "description": "Compare at least two candidates for a job.", "parameters": {"type": "object", "properties": {"job_id": {"type": "string"}, "candidate_ids": {"type": "array", "items": {"type": "string"}}}, "required": ["job_id", "candidate_ids"]}}},
    {"type": "function", "function": {"name": "generate_interview_questions", "description": "Generate exactly three technical questions grounded in the evaluation.", "parameters": {"type": "object", "properties": {"job_id": {"type": "string"}, "candidate_id": {"type": "string"}}, "required": ["job_id", "candidate_id"]}}},
]


def _validate_live_report(
    report: Any,
    request: str,
    expected_job: dict[str, Any],
    expected_evaluations: list[dict[str, Any]],
    job_result: dict[str, Any] | None,
    evaluation_results: dict[str, dict[str, Any]],
    question_results: dict[str, list[str]],
) -> dict[str, Any]:
    if not isinstance(report, dict):
        raise ValueError("LLM returned a non-object report")

    required_fields = {
        "mode",
        "request",
        "job",
        "candidates_evaluated",
        "shortlisted_candidates",
        "human_review_required",
        "note",
    }
    missing_fields = required_fields - report.keys()
    if missing_fields:
        raise ValueError(
            f"LLM report is missing required fields: {', '.join(sorted(missing_fields))}"
        )
    if report["mode"] != "live":
        raise ValueError("LLM report mode must be 'live'")
    if report["request"] != request:
        raise ValueError("LLM report request does not match the submitted request")
    if report["job"] != expected_job:
        raise ValueError("LLM report job does not match the selected job data")
    if job_result != expected_job:
        raise ValueError("Job retrieval tool was not successfully called")
    if report["human_review_required"] is not True:
        raise ValueError("LLM report must set human_review_required to true")
    if not isinstance(report["note"], str) or not report["note"].strip():
        raise ValueError("LLM report note must be a non-empty string")

    returned_evaluations = report["candidates_evaluated"]
    if not isinstance(returned_evaluations, list):
        raise ValueError("LLM report candidates_evaluated must be a list")

    expected_by_id = {
        evaluation["candidate_id"]: evaluation
        for evaluation in expected_evaluations
    }
    returned_by_id: dict[str, dict[str, Any]] = {}
    for evaluation in returned_evaluations:
        if not isinstance(evaluation, dict):
            raise ValueError("Each LLM candidate evaluation must be an object")
        candidate_id = evaluation.get("candidate_id")
        if not isinstance(candidate_id, str) or candidate_id not in expected_by_id:
            raise ValueError("LLM report contains an unknown candidate evaluation")
        if candidate_id in returned_by_id:
            raise ValueError(f"LLM report contains duplicate candidate: {candidate_id}")
        required_evaluation_fields = set(expected_by_id[candidate_id])
        missing_evaluation_fields = required_evaluation_fields - evaluation.keys()
        if missing_evaluation_fields:
            raise ValueError(
                f"LLM evaluation for {candidate_id} is missing fields: "
                f"{', '.join(sorted(missing_evaluation_fields))}"
            )
        if (
            not isinstance(evaluation.get("candidate_name"), str)
            or any(
                not isinstance(evaluation.get(field), list)
                or any(not isinstance(value, str) for value in evaluation[field])
                for field in (
                    "matched_mandatory_skills",
                    "missing_mandatory_skills",
                    "matched_preferred_skills",
                )
            )
            or not isinstance(evaluation.get("experience_summary"), str)
            or isinstance(evaluation.get("match_percentage"), bool)
            or not isinstance(evaluation.get("match_percentage"), (int, float))
            or not isinstance(evaluation.get("explanation"), str)
            or not isinstance(evaluation.get("recommendation"), str)
            or not isinstance(evaluation.get("evidence"), dict)
        ):
            raise ValueError(
                f"LLM evaluation for {candidate_id} has invalid field types"
            )
        if evaluation != expected_by_id[candidate_id]:
            raise ValueError(
                f"LLM evaluation for {candidate_id} does not match deterministic tool output"
            )
        if evaluation_results.get(candidate_id) != expected_by_id[candidate_id]:
            raise ValueError(
                f"Deterministic evaluation tool was not successfully called for {candidate_id}"
            )
        returned_by_id[candidate_id] = evaluation

    if set(returned_by_id) != set(expected_by_id):
        raise ValueError("LLM report must include every selected candidate exactly once")

    expected_shortlist_ids = {
        candidate_id
        for candidate_id, evaluation in expected_by_id.items()
        if evaluation["recommendation"] == "Shortlist"
    }
    returned_shortlist = report["shortlisted_candidates"]
    if not isinstance(returned_shortlist, list):
        raise ValueError("LLM report shortlisted_candidates must be a list")
    returned_shortlist_by_id: dict[str, dict[str, Any]] = {}
    for candidate in returned_shortlist:
        if not isinstance(candidate, dict):
            raise ValueError("Each shortlisted candidate must be an object")
        candidate_id = candidate.get("candidate_id")
        if (
            not isinstance(candidate_id, str)
            or candidate_id not in expected_shortlist_ids
        ):
            raise ValueError(
                "LLM report shortlisted_candidates must contain only deterministic shortlists"
            )
        if candidate_id in returned_shortlist_by_id:
            raise ValueError(f"LLM report contains duplicate shortlist: {candidate_id}")
        expected_evaluation = expected_by_id[candidate_id]
        questions = candidate.get("interview_questions")
        if (
            candidate.get("candidate_name") != expected_evaluation["candidate_name"]
            or not isinstance(questions, list)
            or len(questions) != 3
            or any(not isinstance(question, str) or not question.strip() for question in questions)
            or question_results.get(candidate_id) != questions
        ):
            raise ValueError(
                f"LLM interview questions for {candidate_id} must match exactly "
                "three questions returned by the deterministic tool"
            )
        returned_shortlist_by_id[candidate_id] = candidate

    if set(returned_shortlist_by_id) != expected_shortlist_ids:
        raise ValueError(
            "LLM report must include interview questions for every deterministic shortlist"
        )

    validated_report = {
        "mode": "live",
        "request": request,
        "job": expected_job,
        "candidates_evaluated": expected_evaluations,
        "shortlisted_candidates": [
            {
                "candidate_id": candidate_id,
                "candidate_name": expected_by_id[candidate_id]["candidate_name"],
                "interview_questions": question_results[candidate_id],
            }
            for candidate_id in expected_by_id
            if candidate_id in expected_shortlist_ids
        ],
        "human_review_required": True,
        "note": (
            "Live report uses deterministic Python tools for candidate scores and "
            "interview questions. A human recruiter must make every final decision."
            ),
    }
    return validated_report


class RecruitmentAgent:
    def __init__(self, tools: RecruitmentTools | None = None) -> None:
        self.tools = tools or RecruitmentTools()
        self.tool_map = {
            "get_job_description": self.tools.get_job_description,
            "get_candidate_profiles": self.tools.get_candidate_profiles,
            "search_candidates": self.tools.search_candidates,
            "evaluate_candidate": self.tools.evaluate_candidate,
            "compare_candidates": self.tools.compare_candidates,
            "generate_interview_questions": self.tools.generate_interview_questions,
        }

    def _demo_report(self, request: str, job_id: str, candidate_ids: list[str]) -> dict[str, Any]:
        evaluations = [self.tools.evaluate_candidate(job_id, candidate_id) for candidate_id in candidate_ids]
        evaluations = sorted(evaluations, key=lambda item: item["match_percentage"], reverse=True)
        shortlisted = [item for item in evaluations if item["recommendation"] == "Shortlist"]
        return {"mode": "demo", "request": request, "job": self.tools.get_job_description(job_id), "candidates_evaluated": evaluations, "shortlisted_candidates": [{"candidate_id": item["candidate_id"], "candidate_name": item["candidate_name"], "interview_questions": self.tools.generate_interview_questions(job_id, item["candidate_id"])} for item in shortlisted], "human_review_required": True, "note": "Demo mode uses deterministic local tools. Configure OPENAI_API_KEY for live agent reasoning."}

    def run(self, request: str, job_id: str, candidate_ids: list[str] | None = None) -> dict[str, Any]:
        if not request.strip():
            raise ValueError("Recruitment request cannot be empty")
        job = self.tools.get_job_description(job_id)
        candidates = (
            [item["id"] for item in self.tools.get_candidate_profiles()]
            if candidate_ids is None
            else candidate_ids
        )
        if not candidates:
            raise ValueError("No candidates are available")
        if len(candidates) != len(set(candidates)):
            raise ValueError("Candidate IDs must be unique")
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            return self._demo_report(request, job_id, candidates)
        try:
            expected_evaluations = [
                self.tools.evaluate_candidate(job_id, candidate_id)
                for candidate_id in candidates
            ]
            expected_by_id = {
                evaluation["candidate_id"]: evaluation
                for evaluation in expected_evaluations
            }
            expected_shortlist_ids = {
                candidate_id
                for candidate_id, evaluation in expected_by_id.items()
                if evaluation["recommendation"] == "Shortlist"
            }
            from openai import OpenAI

            client = OpenAI(api_key=api_key, base_url=os.getenv("OPENAI_BASE_URL") or None)
            system_prompt = (
                "You are a careful recruitment decision-support agent. Use tools for all "
                "candidate and job facts; do not invent qualifications or scores. "
                "Evaluate every selected candidate using evaluate_candidate and retrieve "
                "the selected job using get_job_description. For every candidate whose "
                "deterministic recommendation is Shortlist, call "
                "generate_interview_questions. Return a valid JSON object with keys mode "
                "(value 'live'), request (exact submitted text), job (the complete job "
                "tool result), candidates_evaluated (the complete evaluation tool results), "
                "shortlisted_candidates (objects with candidate_id, candidate_name, and "
                "the exact interview_questions returned by the tool), "
                "human_review_required (true), and a non-empty note. Do not modify tool "
                "results. Recommendations are "
                "decision support only; a human recruiter must make every final "
                "employment decision."
            )
            messages: list[dict[str, Any]] = [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": (
                        f"Job ID: {job_id}. Candidate IDs: {', '.join(candidates)}. "
                        f"Request: {request}"
                    ),
                },
            ]
            evaluation_results: dict[str, dict[str, Any]] = {}
            question_results: dict[str, list[str]] = {}
            job_result: dict[str, Any] | None = None
            for _ in range(8):
                response = client.chat.completions.create(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), messages=messages, tools=TOOL_SCHEMAS, tool_choice="auto", temperature=0)
                message = response.choices[0].message
                tool_calls = message.tool_calls or []
                messages.append(message.model_dump(exclude_none=True))
                if not tool_calls:
                    content = message.content or ""
                    try:
                        report = json.loads(content)
                    except json.JSONDecodeError as exc:
                        raise ValueError("LLM returned malformed JSON") from exc
                    return _validate_live_report(
                        report,
                        request,
                        job,
                        expected_evaluations,
                        job_result,
                        evaluation_results,
                        question_results,
                    )
                for tool_call in tool_calls:
                    name = tool_call.function.name
                    if name not in self.tool_map:
                        raise ValueError(f"Unknown tool requested by LLM: {name}")
                    arguments = json.loads(tool_call.function.arguments or "{}")
                    logger.info("Agent tool call: %s", name)
                    try:
                        result = self.tool_map[name](**arguments)
                    except Exception as exc:
                        result = {"error": str(exc)}
                    if (
                        name == "evaluate_candidate"
                        and arguments.get("job_id") == job_id
                        and isinstance(result, dict)
                    ):
                        candidate_id = result.get("candidate_id")
                        if (
                            isinstance(candidate_id, str)
                            and candidate_id in expected_by_id
                        ):
                            evaluation_results[candidate_id] = result
                    elif name == "get_job_description" and isinstance(result, dict):
                        if result.get("id") == job_id:
                            job_result = result
                    elif name == "generate_interview_questions" and isinstance(
                        result, list
                    ):
                        candidate_id = arguments.get("candidate_id")
                        if (
                            arguments.get("job_id") == job_id
                            and isinstance(candidate_id, str)
                            and candidate_id in expected_shortlist_ids
                        ):
                            question_results[candidate_id] = result
                    messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(result)})
            raise RuntimeError("Agent exceeded the maximum tool-calling iterations")
        except ValueError:
            raise
        except Exception as exc:
            logger.exception("Agent API failure")
            raise RuntimeError(f"LLM API error: {exc}") from exc
