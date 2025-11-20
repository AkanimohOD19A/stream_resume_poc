import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="My Progress", page_icon="📊", layout="wide")

if "username" not in st.session_state or not st.session_state.username:
    st.warning("Please set your username on the Home page first.")
    st.stop()

st.title(f"📊 Progress for {st.session_state.username}")

# Initialize REST client
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
headers = {
    "apikey": key,
    "Authorization": f"Bearer {key}"
}

try:
    # Get user stats
    stats_response = requests.get(
        f"{url}/rest/v1/user_stats?username=eq.{st.session_state.username}",
        headers=headers
    )

    if stats_response.status_code == 200 and stats_response.json():
        stats = stats_response.json()[0]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Score", stats["total_score"])
        with col2:
            st.metric("Challenges Completed", stats["challenges_completed"])
        with col3:
            st.metric("Total Time", f"{stats['total_time']:.1f}s")
    else:
        st.info("Complete your first challenge to see stats!")

    st.markdown("---")

    # Get detailed progress
    progress_response = requests.get(
        f"{url}/rest/v1/user_progress?username=eq.{st.session_state.username}&order=completed_at.desc",
        headers=headers
    )

    if progress_response.status_code == 200 and progress_response.json():
        progress = progress_response.json()

        st.subheader("📝 Completed Challenges")

        df = pd.DataFrame(progress)
        df = df[["question_title", "score", "duration", "passed_tests", "total_tests", "completed_at"]]
        df.columns = ["Challenge", "Score", "Time (s)", "Passed", "Total", "Completed At"]

        st.dataframe(df, use_container_width=True)
    else:
        st.info("No challenges completed yet. Start coding! 🚀")

except Exception as e:
    st.error(f"Failed to load progress: {e}")