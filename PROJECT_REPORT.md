# 1. Project Overview
## Project Title
AI HR Recruitment Assistant

## Problem Statement
Recruitment screening can be slow and inconsistent when evidence is scattered across profiles. Recruiters need support that retrieves relevant facts, exposes skill gaps, and keeps the human recruiter accountable for the final decision.

## Brief Description of the Project
This is a Python and Streamlit recruitment decision-support application. An OpenAI-compatible model is provided with six recruitment tools and can decide which tools to call, receive their results, and return a structured report. The application supports two execution modes. Demo mode uses deterministic local tools and does not require a paid provider account. Live provider mode can be enabled through `OPENAI_API_KEY` stored in the local `.env` file.

## IBM Requirement Verification
| Requirement | Evidence in implementation | Verification status |
|---|---|---|
| Project title | This report, `app.py`, and README | Verified |
| Problem statement | This section and README | Verified |
| Brief project description | This section and README | Verified |

# 2. Objectives & Proposed Solution
## Project Objectives
- Build a working OpenAI-compatible tool-calling recruitment agent.
- Ground evaluations in structured local job and candidate evidence.
- Make match scoring reproducible and explainable.
- Support candidate comparison and exactly three technical questions for each shortlisted candidate.
- Keep the final hiring decision with a human recruiter.

## How the Agentic AI Solution Works
1. The recruiter selects a job, candidates, and submits a request in Streamlit.
2. `RecruitmentAgent` validates the request and job, then checks `OPENAI_API_KEY`.
3. In live mode, the OpenAI-compatible model receives six tool schemas and may request retrieval, evaluation, comparison, or interview-question tools.
4. Python executes requested tools and returns their results to the model. Tool names are logged without secrets.
5. The tool-calling loop is bounded at eight iterations. The final provider message must be a JSON object.
6. In demo mode, Python runs deterministic local tools and labels the report `mode: demo`; this does not claim LLM reasoning.
7. `src/scoring.py` calculates match percentages using mandatory skills (60%), preferred skills (20%), experience (15%), and related education (5%).

Live provider verification was not completed because the configured API account had insufficient credits. Therefore, live provider execution and live tool-call verification are not claimed as verified. Offline tests verify that mocked live reports meet a strict field contract and that reported scores, recommendations, evidence, and interview questions agree with successful deterministic tool results; they do not verify real provider behavior.

## Key Features
- `get_job_description()`
- `get_candidate_profiles()`
- `search_candidates()`
- `evaluate_candidate()`
- `compare_candidates()`
- `generate_interview_questions()`
- Lexical RAG-style retrieval over local JSON data rather than sending the full database to every search.
- Evidence fields for mandatory skills, preferred skills, experience, projects, education, certifications, strengths, and missing skills.
- Streamlit job selection, candidate selection, comparison table, skill gaps, scores, explanations, interview questions, and final JSON report.
- Validation for empty requests, invalid IDs, empty searches, insufficient comparison candidates, missing data, malformed JSON, unknown tools, API failures, and excessive tool-loop iterations.
- Human-review warning shown in the UI and `human_review_required: true` in reports.

## IBM Requirement Verification
| Requirement | Evidence in implementation | Verification status |
|---|---|---|
| Objectives stated | Objectives above and README | Verified |
| Agentic solution explained | Tool schemas and bounded loop in `src/agent.py` | Implemented; live execution not provider-verified |
| Key features stated | Six tools, retrieval, scoring, UI, safeguards | Verified locally |

# 3. Implementation & Results
## Technologies/Tools Used
Python 3.14 runtime used for verification, Streamlit, OpenAI Python SDK, `python-dotenv`, pytest, JSON local data, PowerShell, and Mermaid architecture diagrams. Dependencies are declared in `requirements.txt`; secrets are expected in `.env` and are excluded by `.gitignore`.

## Working Process
The repository and data model were implemented first, followed by lexical retrieval, deterministic scoring, tools, the agent loop, Streamlit UI, tests, and documentation. The deterministic slice was tested before the UI. The final app was launched with `streamlit run app.py --server.headless true --server.port 8503` and returned the expected local workflow.

## Screenshots/Output
No screenshot is fabricated or stored. Capture the running Streamlit UI using the steps in `DEMO_CHECKLIST.md`. The latest local checks completed with 21 passing tests and successful compilation. The scenario runner returned deterministic demo reports with the expected scores, recommendations, and skill gaps; its empty-request case reported `ValueError: Recruitment request cannot be empty`.

## Results Achieved
The following results were produced by the local deterministic execution on 2026-10-07:

| Scenario | Actual result |
|---|---|
| Software Engineer recruitment | Maya Patel: 95.0%, Shortlist; Samir Khan: 48.5%, Do not shortlist; Samir missing SQL and Unit Testing |
| Software Engineer comparison | Maya Patel: 95.0%, Shortlist; Jonah Williams: 44.0%, Do not shortlist |
| Data Engineer recruitment | Jonah Williams: 78.0%, Review, missing Apache Airflow; Maya Patel: 44.0%, Do not shortlist, missing ETL, Apache Airflow, and Data Warehousing |
| Backend Engineer recruitment | Elena Rossi: 76.0%, Review, missing PostgreSQL and Distributed Systems; Maya Patel: 56.0%, Review, missing PostgreSQL and Distributed Systems |
| Candidate comparison | Candidates are sorted by deterministic match percentage; Maya ranks above Samir for Software Engineer |
| Candidate with missing mandatory skills | Missing mandatory skills are explicitly reported; Jonah lacks Apache Airflow for Data Engineer |
| Invalid input | Empty request raises `ValueError: Recruitment request cannot be empty` |
| Automated tests | 21 tests passed |
| Syntax/import compilation | `compileall: PASS` |
| Streamlit launch and UI | Local URL `http://localhost:8503` returned HTTP 200; the UI rendered its controls, completed both required demo analyses, and displayed score, recommendation, skill-gap, evidence, question, and report details |

These are local deterministic results. No live LLM result, API latency, provider quality, or live tool-selection claim is made; live provider verification was not completed because the configured API account had insufficient credits.

## IBM Requirement Verification
| Requirement | Actual evidence | Verification status |
|---|---|---|
| Technologies/tools used | Requirements, imports, and successful compilation | Verified |
| Working process | Source code, tests, scenario runner, and app launch | Verified locally |
| Screenshots/output | Output above; screenshots still need to be captured manually | Output verified; screenshots pending |
| Results achieved | Test and scenario results above | Verified locally |

# 4. Conclusion & Future Scope
## Project Conclusion
The project delivers a runnable recruitment decision-support workflow with local structured evidence, retrieval, six callable Python tools, transparent deterministic scoring, a Streamlit interface, and an OpenAI-compatible live-agent path. The local/demo path is verified. The live provider path is implemented but live provider verification was not completed because the configured API account had insufficient credits.

## Challenges Faced
- Candidate certifications are retained as certification evidence and are not silently treated as skills; mandatory skill gaps are separately reported from the score-based recommendation.
- Live-agent verification was not completed because the configured API account had insufficient credits; no live provider execution or tool-call verification is claimed.

## Future Enhancements
- Run a credentialed live smoke test when valid provider credentials are available.
- Add audited embedding retrieval for synonym and semantic matching.
- Add fairness monitoring, recruiter feedback, authentication, persistence, and access controls.
- Add credentialed provider verification and provider-specific compatibility coverage.

## References
- OpenAI Python SDK: https://github.com/openai/openai-python
- Streamlit documentation: https://docs.streamlit.io/
- NIST AI Risk Management Framework: https://www.nist.gov/itl/ai-risk-management-framework
- IBM watsonx.ai: https://www.ibm.com/watsonx

## Final Verification Boundary
Verified: local data loading, retrieval path, deterministic scoring, six tool implementations, validation cases covered by tests, scenario execution, syntax/import compilation, and Streamlit startup/UI response. Not verified: live API authentication, provider availability, actual LLM tool-choice decisions, live malformed-response handling from a provider, and screenshots captured manually by a presenter.
