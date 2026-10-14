# Test Results

Latest local verification: 2026-10-07, using the project's configured Python environment. Commands were run from the project root. Verification was limited to local and offline tests; live provider verification was not completed because the configured API account had insufficient credits.

| Test case | Input | Expected behavior | Actual behavior | Result | Observations |
|---|---|---|---|---|---|
| Complete Software Engineer candidate | `software-engineer`, `maya-patel` | Evidence-based high score, no mandatory gaps, shortlist | 95.0%, no mandatory gaps, Shortlist | PASS | AWS certification is retained as certification evidence, not silently treated as a skill. |
| Software Engineer candidate with gaps | `software-engineer`, `samir-khan` | Verify exact deterministic score, recommendation, and missing skills | 48.5%, Do not shortlist; missing SQL and Unit Testing | PASS | Score and gaps come from the shared scoring implementation. |
| Software Engineer comparison candidate | `software-engineer`, `jonah-williams` | Verify exact deterministic score, recommendation, and missing skills | 44.0%, Do not shortlist; missing REST APIs, Git, and Unit Testing | PASS | Matches the Software Engineer UI comparison scenario. |
| Data Engineer missing skill | `data-engineer`, `jonah-williams` | Report missing Apache Airflow | Apache Airflow reported missing; score 78.0% | PASS | Preferred skills, experience, and education remain visible in the score. |
| Backend Engineer candidate with gaps | `backend-engineer`, `elena-rossi` | Verify exact deterministic score, recommendation, and missing skills | 76.0%, Review; missing PostgreSQL and Distributed Systems | PASS | Mandatory gaps remain explicit even when the recommendation is Review. |
| Interview generation | `backend-engineer`, `elena-rossi` | Exactly 3 technical questions | Exactly 3 questions returned | PASS | Questions reference stored matched/gap evidence. |
| Demo report | API key removed from test process; `software-engineer`, `maya-patel` | Label mode accurately, require human review, and include 3 questions for shortlisted candidate | `mode: demo`, `human_review_required: true`, 3 questions | PASS | Test removes `OPENAI_API_KEY` from its process environment. |
| Empty and duplicate selections | Blank request; empty and repeated candidate IDs | Reject invalid input instead of silently analyzing a different selection | Clear `ValueError` for each invalid input | PASS | An explicitly empty list no longer defaults to evaluating every candidate. |
| Candidate evidence and retrieval | Maya evaluation; `Snowflake warehouse` search | Return profile evidence and rank relevant stored candidate | Maya project/education/certification evidence returned; Jonah ranked first for Snowflake warehouse query | PASS | Retrieval uses local JSON data and transparent lexical matching. |
| Invalid IDs and empty input | Missing IDs; blank search | Raise clear validation errors | `ValueError` messages identify invalid ID or empty query | PASS | Prevents silent unavailable-data behavior. |
| Candidate comparison | `software-engineer`, Maya + Samir | Sort by deterministic score | Maya ranked above Samir | PASS | Comparison uses the same evaluation function as individual review. |
| Live report validation | Offline constructed response and mocked OpenAI client | Enforce required fields, human-review flag, deterministic evaluations, successful tool calls, and exactly 3 tool-generated questions | Valid mocked flow accepted; missing fields, false review flag, changed scores, invalid questions, and missing tool calls rejected | PASS | Mocked/offline coverage only; no real provider call was made. |

Latest command results:

```text
python -m pytest -q
21 passed

python -m compileall -q src app.py run_scenarios.py
PASS (exit code 0)

python run_scenarios.py
All five scenarios completed in demo mode; the invalid-request case reported ValueError.
```

The application supports two execution modes. Demo mode uses deterministic local tools and does not require a paid provider account. Live provider mode can be enabled through `OPENAI_API_KEY` stored in the local `.env` file.

Live provider verification was not completed because the configured API account had insufficient credits. Therefore, live provider execution and live tool-call verification are not claimed as verified. Mocked offline tests do not verify provider availability, authentication, or actual model behavior.
