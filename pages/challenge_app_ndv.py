import streamlit as st
import time
from datetime import datetime
from streamlit_monaco_editor import st_monaco

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
if "progress_data" not in st.session_state:
    st.session_state.progress_data = []  # List of completed challenges
if "leaderboard" not in st.session_state:
    st.session_state.leaderboard = {}  # Dict of username -> stats


# --------------------
# Progress Functions
# --------------------
def save_progress(username, q_id, title, passed, total, duration, score):
    st.session_state.progress_data.append({
        "username": username,
        "question_id": q_id,
        "question_title": title,
        "score": score,
        "duration": duration,
        "passed_tests": passed,
        "total_tests": total,
        "created_at": datetime.now().isoformat()
    })

    # Update leaderboard
    if username not in st.session_state.leaderboard:
        st.session_state.leaderboard[username] = {
            "total_score": 0,
            "challenges_completed": 0,
            "total_time": 0
        }

    st.session_state.leaderboard[username]["total_score"] += score
    st.session_state.leaderboard[username]["challenges_completed"] += 1
    st.session_state.leaderboard[username]["total_time"] += duration


def get_leaderboard():
    if not st.session_state.leaderboard:
        return []

    leaderboard_list = []
    for username, stats in st.session_state.leaderboard.items():
        leaderboard_list.append({
            "username": username,
            "total_score": stats["total_score"],
            "challenges_completed": stats["challenges_completed"],
            "total_time": round(stats["total_time"], 2)
        })

    # Sort by score desc, then time asc
    leaderboard_list.sort(key=lambda x: (-x["total_score"], x["total_time"]))
    return leaderboard_list


# --------------------
# Load Questions
# --------------------
def get_questions():
    return [
        {
            "id": 1,
            "title": "Sum Two Numbers",
            "difficulty": "Easy",
            "desc": "Write a function that takes two integers and returns their sum.",
            "starter": "def add_numbers(a, b):\n    # TODO: Implement the function\n    pass",
            "hints": [
                "Use the + operator to add two numbers",
                "Return the result using the return statement"
            ],
            "tests": [
                {"input": {"a": 2, "b": 3}, "expected": 5},
                {"input": {"a": -1, "b": 1}, "expected": 0},
                {"input": {"a": 0, "b": 0}, "expected": 0},
            ],
            "solution": "def add_numbers(a, b):\n    return a + b",
        },
        {
            "id": 2,
            "title": "Find Maximum",
            "difficulty": "Easy",
            "desc": "Return the maximum number in a list.",
            "starter": "def find_max(nums):\n    # TODO: Implement the function\n    pass",
            "hints": [
                "You can use Python's built-in max() function",
                "Or iterate through the list to find the largest value"
            ],
            "tests": [
                {"input": {"nums": [1, 2, 3]}, "expected": 3},
                {"input": {"nums": [-5, 0, 5]}, "expected": 5},
                {"input": {"nums": [100]}, "expected": 100},
            ],
            "solution": "def find_max(nums):\n    return max(nums)",
        },
        {
            "id": 3,
            "title": "Check Palindrome",
            "difficulty": "Medium",
            "desc": "Return True if a given string is a palindrome (reads the same forwards and backwards).",
            "starter": "def is_palindrome(s):\n    # TODO: Implement the function\n    pass",
            "hints": [
                "Use string slicing: s[::-1] reverses a string",
                "Compare the original string with its reverse",
                "Consider case sensitivity"
            ],
            "tests": [
                {"input": {"s": "racecar"}, "expected": True},
                {"input": {"s": "hello"}, "expected": False},
                {"input": {"s": "A"}, "expected": True},
            ],
            "solution": "def is_palindrome(s):\n    return s == s[::-1]",
        },
    ]


questions = get_questions()
total_questions = len(questions)


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
# UI
# --------------------
st.title("🏁 Progressive Coding Challenge")

# Progress indicator
progress_val = st.session_state.current_q_index / total_questions
st.progress(progress_val, text=f"Challenge {st.session_state.current_q_index + 1} of {total_questions}")

current = questions[st.session_state.current_q_index]

# Two column layout
col_left, col_right = st.columns([3, 2])

# ---------- LEFT PANEL ----------
with col_left:
    st.subheader(f"📘 {current['title']} ({current['difficulty']})")
    st.write(current["desc"])

    # Hints section
    if "hints" in current:
        with st.expander("💡 Hints"):
            for hint in current["hints"]:
                st.write(f"• {hint}")

    st.divider()

    # Monaco Editor
    st.markdown("### 💻 Live Coding Editor")
    user_code = st_monaco(
        value=current["starter"],
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
            save_progress(
                st.session_state.username,
                current["id"],
                current["title"],
                passed,
                total,
                duration,
                score
            )

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
                        st.code(f"Input: {r['input']}\nExpected: {r['expected']}\nGot: {r['actual']}", language="python")
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
st.caption("💡 Progress is stored in session state and will reset when you refresh the page.")