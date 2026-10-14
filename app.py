import logging

import streamlit as st

from src.agent import RecruitmentAgent
from src.repository import RecruitmentRepository

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

st.set_page_config(page_title="AI HR Recruitment Assistant", page_icon="HR", layout="wide")
st.title("AI HR Recruitment Assistant")
st.caption("Agentic recruitment decision support with evidence-based scoring")
st.warning("Responsible AI: this system supports recruiter review only. A human recruiter must make the final employment decision.")

repository = RecruitmentRepository()
jobs = repository.get_jobs()
job_labels = {f"{job.title} | {job.location}": job.id for job in jobs}
selected_label = st.selectbox("Select a job", list(job_labels))
job_id = job_labels[selected_label]
candidates = repository.get_candidates()
candidate_labels = {f"{candidate.name} | {candidate.headline}": candidate.id for candidate in candidates}
selected_labels = st.multiselect("Candidates to evaluate", list(candidate_labels), default=list(candidate_labels)[:2])
request = st.text_area("Recruitment request", value="Evaluate the selected candidates for this role, compare their evidence, and recommend who should advance.")

if st.button("Run recruitment analysis", type="primary", disabled=not selected_labels):
    try:
        with st.spinner("Agent is retrieving evidence and evaluating candidates..."):
            report = RecruitmentAgent().run(request, job_id, [candidate_labels[label] for label in selected_labels])
        st.success(f"Analysis complete in {report.get('mode', 'unknown')} mode")
        evaluations = report.get("candidates_evaluated", [])
        if evaluations:
            st.subheader("Candidate comparison")
            comparison_rows = [
                {
                    "Candidate": item.get("candidate_name"),
                    "Match %": item.get("match_percentage"),
                    "Recommendation": item.get("recommendation"),
                    "Missing mandatory": ", ".join(
                        item.get("missing_mandatory_skills", [])
                    )
                    or "None",
                }
                for item in evaluations
            ]
            st.dataframe(comparison_rows, width="stretch", hide_index=True)
            for item in evaluations:
                with st.expander(f"{item.get('candidate_name', item.get('candidate_id'))} | {item.get('match_percentage', 'n/a')}%"):
                    st.write(item.get("explanation", ""))
                    st.write("Matched mandatory:", ", ".join(item.get("matched_mandatory_skills", [])) or "None")
                    st.write("Matched preferred:", ", ".join(item.get("matched_preferred_skills", [])) or "None")
                    st.write("Evidence:", item.get("evidence", {}))
        for shortlisted in report.get("shortlisted_candidates", []):
            st.subheader(f"Interview questions: {shortlisted.get('candidate_name')}")
            for index, question in enumerate(shortlisted.get("interview_questions", []), 1):
                st.write(f"{index}. {question}")
        with st.expander("Final structured report"):
            st.json(report)
    except Exception as exc:
        st.error(str(exc))

with st.expander("Available jobs and local data"):
    st.json({"jobs": [job.id for job in jobs], "candidate_count": len(candidates)})
