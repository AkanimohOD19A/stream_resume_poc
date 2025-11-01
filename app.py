import streamlit as st
from datetime import datetime
import json
import random
from utils_calibration import extract_text_from_pdf, extract_text_from_docx, analyze_resume_strengths, generate_calibration_test, evaluate_answer

# --- PAGE CONFIG ---
st.set_page_config(page_title="Skill Calibration | CodeSprint", page_icon="🎯", layout="wide")

# st.title("🧭 Calibration")

username = st.text_input("Enter your name to begin:")
# start = st.button("Start Challenges")



# --- SESSION STATE INIT ---

if 'stage' not in st.session_state:
    st.session_state.stage = 'upload'
if 'resume_text' not in st.session_state:
    st.session_state.resume_text = ""
if 'job_description' not in st.session_state:
    st.session_state.job_description = ""
if 'strengths' not in st.session_state:
    st.session_state.strengths = []
if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'scores' not in st.session_state:
    st.session_state.scores = []

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Settings")
    st.info("Groq API key required for AI-based analysis")
    groq_api_key = st.text_input("Groq API Key", type="password", help="Get it at https://console.groq.com")

    st.markdown("---")
    st.header("📍 Stages")
    st.markdown("1️⃣ Upload Resume\n\n 2️⃣ Extract Skills\n\n 3️⃣ Calibration Test\n\n 4️⃣ Path Recommendation")

    if st.button("🏠 Restart"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

if not groq_api_key:
    st.warning("Please enter your Groq API key to continue.")
    st.stop()

# --- STAGE 1: Resume Upload ---
if st.session_state.stage == 'upload':
    st.title("📄 Step 1: Upload Your Resume")

    uploaded = st.file_uploader("Upload Resume (PDF/DOCX)", type=['pdf', 'docx'])
    job_desc = st.text_area("Optional: Paste Job Description", placeholder="Paste the JD here...")

    if uploaded:
        with st.spinner("Extracting resume text..."):
            if uploaded.type == "application/pdf":
                resume_text = extract_text_from_pdf(uploaded)
            else:
                resume_text = extract_text_from_docx(uploaded)

            st.session_state.resume_text = resume_text
            st.success("✅ Resume uploaded successfully!")

            with st.expander("📖 Preview Extracted Text"):
                st.text_area("Extracted Resume Text", resume_text, height=250, disabled=True)

            st.session_state.job_description = job_desc

            if st.button("➡️ Analyze Strengths", type="primary"):
                st.session_state.stage = 'assess'
                st.rerun()

# --- STAGE 2: Analyze Strengths ---
elif st.session_state.stage == 'assess':
    st.title("🎯 Step 2: Skill & Strength Profiling")

    if not st.session_state.strengths:
        with st.spinner("Analyzing resume for skill areas..."):
            st.session_state.strengths = analyze_resume_strengths(st.session_state.resume_text, groq_api_key)

    if st.session_state.strengths:
        st.subheader("Top Skills & Strength Areas")
        for s in st.session_state.strengths:
            st.markdown(f"**• {s['strength']}** — {s['explanation']}")

        if st.button("➡️ Take Calibration Test", type="primary"):
            st.session_state.stage = 'test'
            st.rerun()

# --- STAGE 3: Calibration Test ---
elif st.session_state.stage == 'test':
    st.title("🧠 Step 3: Calibration Test")

    if not st.session_state.questions:
        with st.spinner("Generating calibration questions..."):
            st.session_state.questions = generate_calibration_test(st.session_state.strengths, groq_api_key)

    st.info("Answer the following short coding or conceptual questions:")

    for i, q in enumerate(st.session_state.questions, 1):
        with st.expander(f"Question {i}: {q['topic']} ({q['difficulty']})", expanded=i == 1):
            st.markdown(f"**{q['question']}**")
            ans = st.text_area("Your Answer", key=f"ans_{i}")

            if st.button(f"Evaluate {i}", key=f"eval_{i}"):
                with st.spinner("Evaluating your response..."):
                    result = evaluate_answer(q['question'], ans, groq_api_key)
                    st.session_state.scores.append(result['score'])
                    st.success(f"✅ Score: {result['score']}/10 — {result['feedback']}")

    if st.button("➡️ See Skill Path Recommendation", type="primary"):
        st.session_state.stage = 'summary'
        st.rerun()

# --- STAGE 4: Summary & Recommendation ---
elif st.session_state.stage == 'summary':
    st.title("🏁 Step 4: Your Skill Path Recommendation")

    if st.session_state.scores:
        avg = sum(st.session_state.scores) / len(st.session_state.scores)
        st.metric("Average Calibration Score", f"{avg:.1f}/10")

        if avg >= 8:
            level = "Advanced"
        elif avg >= 5:
            level = "Intermediate"
        else:
            level = "Beginner"

        st.success(f"🎯 Your recommended starting path: **{level} Level Challenges**")

        st.markdown("""
        - **Beginner:** Start with Microtasks (5 min)
        - **Intermediate:** Start with Mini Challenges (15 min)
        - **Advanced:** Begin with Major Problem Sets
        """)


        if st.button("🚀 Proceed to Challenges"):
            if username.strip() == "":
                st.warning("Please enter a valid username.")
            else:
                st.session_state["username"] = username
                st.session_state["current_q_index"] = 0
                st.session_state["test_results"] = []
                st.switch_page("pages/challenge_app.py")
            # st.switch_page("pages/challenge_app.py")

st.markdown("---")
st.caption("© CodeSprint | Powered by Streamlit & Groq AI")
