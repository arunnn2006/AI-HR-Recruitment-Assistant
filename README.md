# AI HR Recruitment Assistant

## Project overview
An Agentic AI recruitment decision-support application for retrieving job and candidate evidence, evaluating fit transparently, comparing candidates, and creating technical interview questions.

## Problem statement
Recruiters need repeatable shortlisting support without relying on opaque, invented, or inconsistent candidate assessments. This project combines an OpenAI-compatible tool-calling agent with deterministic Python scoring and a local recruitment knowledge base.

## Objectives
- Retrieve relevant local evidence instead of sending the full database to the model.
- Let the agent choose and call recruitment tools.
- Keep match percentages reproducible and separate from LLM prose.
- Provide a demonstrable Streamlit workflow with responsible-AI safeguards.

## Architecture and agent behavior
The agent receives a recruiter request, job ID, and candidate IDs. It can call `get_job_description`, `get_candidate_profiles`, `search_candidates`, `evaluate_candidate`, `compare_candidates`, and `generate_interview_questions`. Python executes each call, returns the result to the LLM, and continues until the LLM returns a JSON report. See [ARCHITECTURE.md](ARCHITECTURE.md).

Local lexical retrieval ranks records by query/skill token overlap and is intentionally transparent. Deterministic scoring uses mandatory skills (60%), preferred skills (20%), experience (15%), and related education (5%).

## Technologies
Python, Streamlit, OpenAI Python SDK, python-dotenv, pytest, JSON, Mermaid.

## Installation and environment
```powershell
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```
The application supports two execution modes. Demo mode uses deterministic local tools and does not require a paid provider account. Live provider mode can be enabled through `OPENAI_API_KEY` stored in the local `.env` file; `OPENAI_BASE_URL` and `OPENAI_MODEL` configure an OpenAI-compatible provider. Keep `.env` local and do not share or commit it.

## Demo mode and live LLM mode
**Demo mode** is selected when `OPENAI_API_KEY` is absent or empty. It uses the same local recruitment tools and deterministic Python scoring, labels the report `mode: demo`, and does not claim LLM reasoning.

**Live LLM mode** requires a valid provider key and a provider that supports chat-completion tool calling. The model can use the recruitment tools and returns a report labeled `mode: live` only after a provider response passes report validation. Candidate evaluations and interview questions must match successful deterministic Python tool results; malformed or inconsistent reports are rejected. Live provider verification was not completed because the configured API account had insufficient credits. Therefore, live provider execution and live tool-call verification are not claimed as verified. Offline tests exercise the validation and mocked tool-calling flow, not a real provider.

## Run
```powershell
streamlit run app.py
```
Open the local Streamlit URL. The UI displays the actual execution mode and keeps the human-review warning visible.

## Sample use cases
Use the included Software Engineer, Data Engineer, and Backend Engineer roles. Try Maya Patel for Software Engineer, Jonah Williams for the Data Engineer missing-Airflow case, and Elena Rossi for Backend Engineer. `python run_scenarios.py` runs all demonstration scenarios and the invalid-input case.

## Testing
```powershell
python -m pytest -q
python -m compileall -q src app.py run_scenarios.py
```
See [TEST_RESULTS.md](TEST_RESULTS.md) for the latest executed deterministic scenarios.

## Responsible AI
This is decision support, not an autonomous hiring system. The application states that a human recruiter must make the final decision. It uses only stored profile evidence, exposes missing mandatory skills, and keeps deterministic scoring separate from generated explanations. Human review is required before any employment action.

## Limitations and challenges
The local retriever is lexical rather than embedding-based, so synonyms may not rank well. Live LLM availability, model behavior, and provider tool-calling support can vary. Live provider execution and tool calls have not been verified for this project.

## Future enhancements
Add audited embedding retrieval, recruiter feedback loops, fairness monitoring, authentication, persistence, and credentialed provider contract verification.

## References
- OpenAI Python SDK documentation: https://github.com/openai/openai-python
- Streamlit documentation: https://docs.streamlit.io/
- NIST AI Risk Management Framework: https://www.nist.gov/itl/ai-risk-management-framework
- IBM watsonx.ai Agentic AI concepts: https://www.ibm.com/watsonx
