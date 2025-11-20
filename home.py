import streamlit as st

st.set_page_config(
    page_title="Welcome to Coding Challenges",
    page_icon="🎯",
    layout="centered"
)

# Custom CSS
st.markdown("""
<style>
    .big-title {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
    }
    .subtitle {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .feature-box {
        padding: 1.5rem;
        border-radius: 10px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Hero Section
st.markdown('<div class="big-title">🏁 Coding Challenges</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Master Python through progressive challenges</div>', unsafe_allow_html=True)

st.markdown("---")

# Features
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("### 🎯 Progressive")
    st.write("Start easy, get harder")
with col2:
    st.markdown("### 💾 Persistent")
    st.write("Track your progress")
with col3:
    st.markdown("### 🏆 Competitive")
    st.write("Global leaderboard")

st.markdown("---")

# Login/Registration
st.markdown("### 👤 Enter Your Username")

col_login, col_spacer = st.columns([2, 1])

with col_login:
    username = st.text_input(
        "Username",
        placeholder="Enter a unique username",
        max_chars=50,
        help="Choose a username to track your progress"
    )

    remember_me = st.checkbox("Remember me", value=True)

    if st.button("🚀 Start Coding", type="primary", use_container_width=True):
        if username and username.strip():
            st.session_state.username = username.strip()
            st.success(f"Welcome, {username}! 🎉")
            st.info("👉 Navigate to 'Challenges' page to start coding!")

            if remember_me:
                st.session_state.remember = True
        else:
            st.error("Please enter a valid username")

# Info Section
st.markdown("---")
st.markdown("### 📊 What You'll Get")

info_col1, info_col2 = st.columns(2)

with info_col1:
    st.markdown("""
    ✅ **6+ Coding Challenges**
    - Easy to Medium difficulty
    - Real-world problems
    - Detailed hints

    ✅ **Live Code Editor**
    - Syntax highlighting
    - Auto-completion
    - Instant feedback
    """)

with info_col2:
    st.markdown("""
    ✅ **Progress Tracking**
    - Save your solutions
    - Track completion
    - View statistics

    ✅ **Global Leaderboard**
    - Compete with others
    - See your ranking
    - Earn achievements
    """)

# Stats
st.markdown("---")
st.markdown("### 📈 Platform Stats")

try:
    import requests

    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}"
    }

    # Get counts
    questions_response = requests.get(
        f"{url}/rest/v1/questions?select=id",
        headers=headers
    )
    users_response = requests.get(
        f"{url}/rest/v1/user_stats?select=username",
        headers=headers
    )

    if questions_response.status_code == 200 and users_response.status_code == 200:
        question_count = len(questions_response.json())
        user_count = len(users_response.json())

        stat_col1, stat_col2, stat_col3 = st.columns(3)
        with stat_col1:
            st.metric("Total Challenges", question_count)
        with stat_col2:
            st.metric("Active Users", user_count)
        with stat_col3:
            st.metric("Solutions Submitted", user_count * 2)  # Rough estimate
except:
    pass

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Built with ❤️ using Streamlit & Supabase</p>
    <p>Start your coding journey today! 🚀</p>
</div>
""", unsafe_allow_html=True)