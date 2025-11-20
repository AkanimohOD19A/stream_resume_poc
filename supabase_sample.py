# from supabase import create_client, Client
# import streamlit as st

# url = st.secrets['SUPABASE_URL']
# key = st.secrets['SUPABASE_API_KEY_ANON']
import streamlit as st
import time
from datetime import datetime
from streamlit_monaco_editor import st_monaco
from supabase import create_client, Client


# --------------------
# Supabase Setup
# --------------------
@st.cache_resource
def init_supabase() -> Client:
    """Initialize Supabase client"""
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_API_KEY_ANON"]
    return create_client(url, key)


supabase = init_supabase()

# --------------------
# Page Config
# --------------------
st.set_page_config(
    page_title="Progressive Coding Challenges",
    page_icon="🏁",
    layout="wide"
)

# --------------------
# Session Setup
# --------------------
if ("username" not in st.session_state
        or not st.session_state.username
        or not st.session_state.username.strip()
):
    st.warning("Please return to the calibration page to start properly.")
    st.stop()
else:
    st.success(f"Ready to start {st.session_state.username}")

if "current_q_index" not in st.session_state:
    st.session_state.current_q_index = 0
if "test_results" not in st.session_state:
    st.session_state.test_results = []


# --------------------
# Database Functions
# --------------------

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_questions():
    """Load all questions from Supabase"""
    try:
        response = supabase.table("questions").select("*").order("id").execute()
        return response.data
    except Exception as e:
        st.error(f"Failed to load questions: {e}")
        return []


def get_question_by_id(question_id):
    """Get specific question by ID"""
    try:
        response = supabase.table("questions").select("*").eq("id", question_id).single().execute()
        return response.data
    except Exception as e:
        st.error(f"Failed to load question: {e}")
        return None


def save_progress(username, question_id, title, passed, total, duration, score):
    """Save user progress to Supabase"""
    try:
        # Insert progress record
        progress_data = {
            "username": username,
            "question_id": question_id,
            "question_title": title,
            "score": score,
            "duration": duration,
            "passed_tests": passed,
            "total_tests": total,
            "completed_at": datetime.now().isoformat()
        }
        supabase.table("user_progress").insert(progress_data).execute()

        # Update or create user stats
        existing = supabase.table("user_stats").select("*").eq("username", username).execute()

        if existing.data:
            # Update existing stats
            current = existing.data[0]
            supabase.table("user_stats").update({
                "total_score": current["total_score"] + score,
                "challenges_completed": current["challenges_completed"] + 1,
                "total_time": current["total_time"] + duration,
                "updated_at": datetime.now().isoformat()
            }).eq("username", username).execute()
        else:
            # Create new stats
            supabase.table("user_stats").insert({
                "username": username,
                "total_score": score,
                "challenges_completed": 1,
                "total_time": duration,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }).execute()

        return True
    except Exception as e:
        st.error(f"Failed to save progress: {e}")
        return False


def get_leaderboard(limit=10):
    """Get top users from leaderboard"""
    try:
        response = supabase.table("user_stats") \
            .select("*") \
            .order("total_score", desc=True) \
            .order("total_time", desc=False) \
            .limit(limit) \
            .execute()

        return [{
            "username": entry["username"],
            "total_score": entry["total_score"],
            "challenges_completed": entry["challenges_completed"],
            "total_time": round(entry["total_time"], 2)
        } for entry in response.data]
    except Exception as e:
        st.error(f"Failed to load leaderboard: {e}")
        return []


def get_user_progress(username):
    """Get all progress for a specific user"""
    try:
        response = supabase.table("user_progress") \
            .select("*") \
            .eq("username", username) \
            .order("completed_at", desc=True) \
            .execute()
        return response.data
    except Exception as e:
        st.error(f"Failed to load user progress: {e}")
        return []


def get_user_completed_questions(username):
    """Get list of question IDs user has completed"""
    try:
        response = supabase.table("user_progress") \
            .select("question_id") \
            .eq("username", username) \
            .execute()
        return [entry["question_id"] for entry in response.data]
    except Exception as e:
        return []


# --------------------
# Code Runner
# --------------------
def run_code(user_code, tests):
    results = []
    for idx, case in enumerate(tests):
        try:
            local_vars = {}
            exec(user_code, {}, local_vars)
            # Get the first function defined in the code
            func = list(local_vars.values())[0]
            output = func(**case["input"])
            passed = output == case["expected"]
            results.append({
                "passed": passed,
                "input": case["input"],
                "expected": case["expected"],
                "actual": output
            })
        except Exception as e:
            results.append({"passed": False, "error": str(e), "input": case["input"]})
    return results


# --------------------
# Load Questions
# --------------------
questions = load_questions()
if not questions:
    st.error("No questions available. Please add questions to your Supabase database.")
    st.stop()

total_questions = len(questions)

# Get user's completed questions
completed_ids = get_user_completed_questions(st.session_state.username)

# --------------------
# UI
# --------------------
st.title("🏁 Progressive Coding Challenge")

# Progress indicator
progress_val = st.session_state.current_q_index / total_questions
st.progress(progress_val, text=f"Challenge {st.session_state.current_q_index + 1} of {total_questions}")

current = questions[st.session_state.current_q_index]

# Show completion status
if current["id"] in completed_ids:
    st.info("✅ You've already completed this challenge!")

# Two column layout
col_left, col_right = st.columns([3, 2])

# ---------- LEFT PANEL ----------
with col_left:
    st.subheader(f"📘 {current['title']} ({current['difficulty']})")
    st.write(current["description"])

    # Hints section
    if current.get("hints"):
        with st.expander("💡 Hints"):
            for hint in current["hints"]:
                st.write(f"• {hint}")

    st.divider()

    # Monaco Editor
    st.markdown("### 💻 Live Coding Editor")
    user_code = st_monaco(
        value=current["starter_code"],
        language="python",
        height="400px",
        theme="vs-dark",
        key=f"monaco_editor_{st.session_state.current_q_index}"
    )

    # Buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        run_btn = st.button("▶️ Run Tests", use_container_width=True, type="primary")
    with col2:
        if st.session_state.current_q_index < total_questions - 1:
            skip_btn = st.button("⏭️ Skip", use_container_width=True)
        else:
            skip_btn = False
    with col3:
        if st.button("🔄 Reset Code", use_container_width=True):
            st.rerun()

# ---------- RIGHT PANEL ----------
with col_right:
    st.subheader("📊 Test Results")

    # Handle skip
    if skip_btn:
        st.session_state.current_q_index += 1
        st.session_state.test_results = []
        st.rerun()

    # Run tests
    if run_btn:
        start_time = time.time()
        results = run_code(user_code, current["tests"])
        end_time = time.time()
        duration = round(end_time - start_time, 2)
        passed = sum(1 for r in results if r.get("passed", False))
        total = len(results)
        score = int((passed / total) * 100) if total > 0 else 0
        st.session_state.test_results = results

        # Display summary
        if passed == total:
            st.success(f"✅ All tests passed! Score: {score}/100")
            st.balloons()

            # Save to Supabase
            success = save_progress(
                st.session_state.username,
                current["id"],
                current["title"],
                passed,
                total,
                duration,
                score
            )

            if success:
                st.success("💾 Progress saved to cloud!")
                # Clear cache to refresh leaderboard
                load_questions.clear()

            if st.session_state.current_q_index < total_questions - 1:
                if st.button("➡️ Next Challenge", use_container_width=True, type="primary"):
                    st.session_state.current_q_index += 1
                    st.session_state.test_results = []
                    st.rerun()
            else:
                st.success("🎉 You've completed all challenges!")
        else:
            st.warning(f"⚠️ {passed}/{total} tests passed. Score: {score}/100")

    # Show detailed results
    if st.session_state.test_results:
        st.markdown("### 🧪 Detailed Results")
        for i, r in enumerate(st.session_state.test_results, 1):
            with st.container():
                if r.get("passed", False):
                    st.success(f"**Test {i}** ✅")
                    st.code(f"Input: {r['input']}\nOutput: {r['actual']}", language="python")
                else:
                    st.error(f"**Test {i}** ❌")
                    if 'error' in r:
                        st.code(f"Input: {r.get('input', 'N/A')}\nError: {r['error']}", language="python")
                    else:
                        st.code(f"Input: {r['input']}\nExpected: {r['expected']}\nGot: {r['actual']}",
                                language="python")
                st.divider()
    else:
        st.info("👈 Click 'Run Tests' to see results")
        st.markdown("---")
        st.markdown("**Tips:**")
        st.markdown("• Use proper indentation")
        st.markdown("• Test your code before submitting")
        st.markdown("• Read error messages carefully")

# Leaderboard at bottom
st.markdown("---")
st.subheader("🏆 Leaderboard")
leaderboard = get_leaderboard()
if leaderboard:
    # Create a nice table
    cols = st.columns([1, 3, 2, 2, 2])
    with cols[0]:
        st.markdown("**Rank**")
    with cols[1]:
        st.markdown("**Username**")
    with cols[2]:
        st.markdown("**Score**")
    with cols[3]:
        st.markdown("**Completed**")
    with cols[4]:
        st.markdown("**Time (s)**")

    st.divider()

    for idx, entry in enumerate(leaderboard, 1):
        cols = st.columns([1, 3, 2, 2, 2])
        with cols[0]:
            medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"#{idx}"
            st.write(medal)
        with cols[1]:
            # Highlight current user
            if entry["username"] == st.session_state.username:
                st.markdown(f"**{entry['username']}** 👈")
            else:
                st.write(entry["username"])
        with cols[2]:
            st.write(f"{entry['total_score']}")
        with cols[3]:
            st.write(f"{entry['challenges_completed']}")
        with cols[4]:
            st.write(f"{entry['total_time']}")
else:
    st.info("Complete challenges to appear on the leaderboard!")

# Footer
st.markdown("---")
st.markdown("<center>⚡ Built for skill progression & confidence growth.</center>", unsafe_allow_html=True)
st.caption("💡 Progress is stored in Supabase and persists across sessions.")