from datetime import datetime
from utils import *

# Page config
st.set_page_config(
    page_title="AI Interview Assistant",
    page_icon="💼",
    layout="wide"
)

# Initialize session state
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
if 'interview_history' not in st.session_state:
    st.session_state.interview_history = []



# Main App UI
st.title("💼 AI Interview Assistant")
st.markdown("---")

# Sidebar for API key and navigation
with st.sidebar:
    st.header("⚙️ Settings")
    groq_api_key = st.text_input("Groq API Key", type="password",
                                 help="Get your free API key from https://console.groq.com")

    st.markdown("---")
    st.header("📍 Navigation")

    if st.button("🏠 Start Over"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.markdown("---")
    st.markdown("""
    ### 📋 Process:
    1. Upload Resume
    2. Assess Strengths
    3. Add Job Description
    4. Interview Roleplay
    5. Schedule Live Session
    """)

# Main content area
if not groq_api_key:
    st.warning("⚠️ Please enter your Groq API key in the sidebar to continue")
    st.info("Get your free API key at: https://console.groq.com")
    st.stop()

# Stage 1: Resume Upload
if st.session_state.stage == 'upload':
    st.header("📄 Step 1: Upload Resume")

    col1, col2 = st.columns([2, 1])

    with col1:
        uploaded_file = st.file_uploader(
            "Upload candidate's resume (PDF or DOCX)",
            type=['pdf', 'docx'],
            help="Upload a resume to begin the interview process"
        )

        if uploaded_file:
            with st.spinner("Extracting text from resume..."):
                if uploaded_file.type == "application/pdf":
                    resume_text = extract_text_from_pdf(uploaded_file)
                else:
                    resume_text = extract_text_from_docx(uploaded_file)

                if resume_text:
                    st.session_state.resume_text = resume_text
                    st.success("✅ Resume uploaded successfully!")

                    with st.expander("📖 Preview Resume Text"):
                        st.text_area("Extracted Text", resume_text, height=300, disabled=True)

                    if st.button("➡️ Proceed to Assessment", type="primary"):
                        st.session_state.stage = 'assess'
                        st.rerun()

    with col2:
        st.info("""
        **Supported Formats:**
        - PDF (.pdf)
        - Word Document (.docx)

        **Tips:**
        - Ensure text is readable
        - Avoid scanned images
        - Standard resume format works best
        """)

# Stage 2: Assess Strengths
elif st.session_state.stage == 'assess':
    st.header("🎯 Step 2: Candidate Strength Assessment")

    if not st.session_state.strengths:
        with st.spinner("🔍 Analyzing resume and identifying key strengths..."):
            strengths = analyze_resume_strengths(st.session_state.resume_text, groq_api_key)
            st.session_state.strengths = strengths

    if st.session_state.strengths:
        st.subheader("Top 5 Candidate Strengths")

        for idx, strength in enumerate(st.session_state.strengths, 1):
            with st.expander(f"💪 Strength {idx}: {strength.get('strength', 'N/A')}", expanded=True):
                st.write(strength.get('explanation', 'No explanation provided'))

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Back to Upload"):
                st.session_state.stage = 'upload'
                st.rerun()
        with col2:
            if st.button("➡️ Add Job Description", type="primary"):
                st.session_state.stage = 'job_description'
                st.rerun()

# Stage 3: Job Description
elif st.session_state.stage == 'job_description':
    st.header("📋 Step 3: Job Description")

    job_desc = st.text_area(
        "Enter the Job Description",
        value=st.session_state.job_description,
        height=300,
        placeholder="Paste the complete job description here..."
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Back to Assessment"):
            st.session_state.stage = 'assess'
            st.rerun()
    with col2:
        if st.button("➡️ Generate Interview Questions", type="primary", disabled=not job_desc):
            st.session_state.job_description = job_desc
            st.session_state.stage = 'roleplay'
            st.rerun()

# Stage 4: Interview Roleplay
elif st.session_state.stage == 'roleplay':
    st.header("🎭 Step 4: Interview Roleplay Session")

    # Generate questions if not already generated
    if not st.session_state.questions:
        with st.spinner("🤖 Generating tailored interview questions..."):
            questions = generate_interview_questions(
                st.session_state.resume_text,
                st.session_state.job_description,
                groq_api_key
            )
            st.session_state.questions = questions

    if st.session_state.questions:
        st.success(f"✅ Generated {len(st.session_state.questions)} interview questions")

        # Display questions
        for idx, q in enumerate(st.session_state.questions, 1):
            with st.expander(f"❓ Question {idx}: {q.get('focus_area', 'General')} | {q.get('difficulty', 'Medium')}",
                             expanded=idx == 1):
                st.markdown(f"**{q.get('question', 'N/A')}**")

                # Answer input
                answer_key = f"answer_{idx}"
                answer = st.text_area(
                    "Your Answer:",
                    key=answer_key,
                    height=150,
                    placeholder="Type your answer here..."
                )

                eval_key = f"eval_{idx}"
                if st.button(f"Evaluate Answer {idx}", key=f"btn_{idx}"):
                    if answer:
                        with st.spinner("Evaluating..."):
                            evaluation = evaluate_answer(q.get('question'), answer, groq_api_key)
                            st.session_state[eval_key] = evaluation
                    else:
                        st.warning("Please provide an answer first")

                # Show evaluation if exists
                if eval_key in st.session_state:
                    eval_data = st.session_state[eval_key]
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        score = eval_data.get('score', 0)
                        st.metric("Score", f"{score}/10")
                    with col2:
                        st.info(f"**Feedback:** {eval_data.get('feedback', 'N/A')}")
                        if 'strengths' in eval_data:
                            st.success(f"**Strengths:** {eval_data['strengths']}")
                        if 'improvements' in eval_data:
                            st.warning(f"**Improvements:** {eval_data['improvements']}")

        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Back to Job Description"):
                st.session_state.stage = 'job_description'
                st.rerun()
        with col2:
            if st.button("➡️ Schedule Live Interview", type="primary"):
                st.session_state.stage = 'schedule'
                st.rerun()

# Stage 5: Schedule Live Session
elif st.session_state.stage == 'schedule':
    st.header("📅 Step 5: Schedule Live Coding Interview")

    st.info("🎉 Great work completing the AI interview session!")

    tab1, tab2 = st.tabs(["📋 Session Summary", "📅 Schedule Live Interview"])

    with tab1:
        st.subheader("Interview Summary")

        # Calculate average score
        scores = []
        for idx in range(1, len(st.session_state.questions) + 1):
            eval_key = f"eval_{idx}"
            if eval_key in st.session_state:
                scores.append(st.session_state[eval_key].get('score', 0))

        if scores:
            avg_score = sum(scores) / len(scores)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Questions Answered", len(scores))
            with col2:
                st.metric("Average Score", f"{avg_score:.1f}/10")
            with col3:
                performance = "Excellent" if avg_score >= 8 else "Good" if avg_score >= 6 else "Needs Improvement"
                st.metric("Performance", performance)

        # Export button
        if st.button("📥 Export Interview Transcript"):
            transcript = {
                "date": datetime.now().isoformat(),
                "questions": st.session_state.questions,
                "evaluations": {f"Q{i + 1}": st.session_state.get(f"eval_{i + 1}", {}) for i in
                                range(len(st.session_state.questions))}
            }
            st.download_button(
                "Download JSON",
                data=json.dumps(transcript, indent=2),
                file_name=f"interview_transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

    with tab2:
        st.subheader("Schedule a Live Coding Session with a Peer")

        with st.form("schedule_form"):
            col1, col2 = st.columns(2)

            with col1:
                candidate_name = st.text_input("Candidate Name")
                candidate_email = st.text_input("Candidate Email")
                preferred_date = st.date_input("Preferred Date")

            with col2:
                candidate_phone = st.text_input("Phone Number (optional)")
                preferred_time = st.time_input("Preferred Time")
                interview_type = st.selectbox("Interview Type", ["Live Coding", "System Design", "Behavioral", "Mixed"])

            additional_notes = st.text_area("Additional Notes", placeholder="Any specific topics or requirements...")

            submitted = st.form_submit_button("📧 Submit Scheduling Request", type="primary")

            if submitted:
                if candidate_name and candidate_email:
                    st.success("✅ Scheduling request submitted successfully!")
                    st.balloons()
                    st.info("""
                    **Next Steps:**
                    - You will receive a confirmation email shortly
                    - A peer interviewer will be assigned
                    - Calendar invite will be sent to your email
                    - You can reschedule up to 24 hours before the session
                    """)
                else:
                    st.error("Please fill in required fields (Name and Email)")

        st.markdown("---")
        if st.button("⬅️ Back to Interview"):
            st.session_state.stage = 'roleplay'
            st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>AI Interview Assistant | Powered by Groq AI & Streamlit</p>
</div>
""", unsafe_allow_html=True)