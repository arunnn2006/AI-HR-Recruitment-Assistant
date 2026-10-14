# IBM Project Demo Checklist

Use this checklist to produce a truthful final demonstration. Do not present demo-mode output as live LLM output.

## 1. Environment setup

From the project root:

```powershell
python -m pip install -r requirements.txt
```

Expected output: dependency installation completes without an error.

The application supports two execution modes. Demo mode uses deterministic local tools and does not require a paid provider account; to select it, leave `OPENAI_API_KEY` absent or empty. Live provider mode can be enabled through `OPENAI_API_KEY` stored in the local `.env` file.

For live-agent verification, create `.env` from `.env.example` and set a valid provider key:

```powershell
Copy-Item .env.example .env
# Edit .env and set OPENAI_API_KEY. Do not paste the key into screenshots or source files.
```

Expected live prerequisite: the key is present and the configured OpenAI-compatible provider supports chat-completion tool calling.

## 2. Automated verification

```powershell
python -m pytest -q
```

Expected output:

```text
21 passed
```

Screenshot to capture: terminal showing the passing test count.

```powershell
python -m compileall -q src app.py run_scenarios.py
```

Expected output: no error output and exit code 0. The verification run also printed `compileall: PASS`.

Screenshot to capture: optional terminal view showing the successful command and clean prompt.

## 3. Local scenario demonstration

```powershell
python run_scenarios.py
```

Expected observations:

- Software Engineer: Maya Patel is 95.0% and `Shortlist`; Samir Khan is 48.5% and `Do not shortlist`.
- Data Engineer: Jonah Williams is 78.0% and `Review`; `Apache Airflow` is explicitly missing.
- Backend Engineer: Elena Rossi is 76.0% and `Review`; PostgreSQL and Distributed Systems are explicitly missing.
- An invalid empty request prints a `ValueError` about the request being empty.
- Reports say `mode: demo` when the API key is absent or empty.

Screenshot to capture: terminal sections showing one complete report, the missing-skill case, and the invalid-input case. Avoid capturing any secrets.

## 4. Streamlit UI demonstration

```powershell
streamlit run app.py
```

Open the URL printed by Streamlit. The latest verified instance used `http://localhost:8503`.

Screenshot status: The UI has been inspected interactively, but no screenshot files have been generated or saved. **Manual capture is required** for each item below.

1. [ ] **Manual capture required — Initial UI:** title, description, responsible-AI warning, job/candidate selectors, request box, and analysis button.
2. [ ] **Manual capture required — Software Engineer comparison:** select Maya Patel and Jonah Williams; show their comparison rows, scores, recommendations, and missing mandatory skills.
3. [ ] **Manual capture required — Candidate evidence:** expand a candidate and show explanation, matched mandatory/preferred skills, and evidence.
4. [ ] **Manual capture required — Interview questions:** show exactly three generated questions for shortlisted Maya Patel.
5. [ ] **Manual capture required — Final structured report:** expand the report and show `human_review_required: true` and `mode: demo`.
6. [ ] **Manual capture required — Data Engineer:** select Jonah Williams and show 78%, `Review`, and the missing Apache Airflow gap.

Expected UI behavior: no exceptions, scores match the command-line results, the responsible-AI warning remains visible, and the report is labeled with the actual execution mode.

## 5. Live Agentic AI verification (not completed)

Live provider verification was not completed because the configured API account had insufficient credits. Therefore, live provider execution and live tool-call verification are not claimed as verified. Do not run this section until provider credits are available and live verification is intentionally authorized.

After that prerequisite is met, the following checks can be used for a future live verification:

```powershell
python run_scenarios.py
```

Expected live observations:

- The report field `mode` is `live`.
- The provider makes one or more tool calls before returning the report.
- The final report is JSON and includes `human_review_required: true`.
- Scores match deterministic Python tool results rather than invented percentages.
- Exactly three interview questions appear for each shortlisted candidate.

Screenshot to capture: terminal or UI showing `mode: live`, the final report, and tool-call logging. Redact provider URLs, tokens, personal data not needed for the presentation, and any secret values.

Until live verification is completed with sufficient credits, keep this section marked **NOT VERIFIED**. Do not claim that live tool selection or provider behavior was tested.

## 6. IBM section coverage

- [x] Project Overview: title, problem statement, and brief description are in `PROJECT_REPORT.md`.
- [x] Objectives & Proposed Solution: objectives, agent workflow, six tools, retrieval, scoring, and safeguards are documented.
- [x] Implementation & Results: technologies, working process, real outputs, test results, and screenshot plan are documented.
- [x] Conclusion & Future Scope: conclusion, limitations, references, and future enhancements are documented.
- [x] `ARCHITECTURE.md` is available for diagrams and technical explanation.
- [x] `TEST_RESULTS.md` records the deterministic test cases.

## 7. Remaining issues at this verification point

- Live Agentic AI Verification is **NOT VERIFIED** because the configured API account had insufficient credits. Do not present demo results as live results.
- Screenshots are not generated or fabricated by the repository; the presenter must capture them from the running UI.
- The retriever is transparent lexical matching, so semantic synonyms may not rank as well as an embedding retriever.
- Live report validation requires the documented fields, deterministic evaluation values, successful selected-job/evaluation/question tool calls, human-review flag, and three tool-generated questions. Offline mocked tests cover this logic; real provider behavior remains unverified.