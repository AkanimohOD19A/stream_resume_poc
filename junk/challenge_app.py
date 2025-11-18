import os
import tempfile
import streamlit as st
import sqlite3
import time
import json
from datetime import datetime
from groq import Groq

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
if "ai_assessment" not in st.session_state:
    st.session_state.ai_assessment = None
if "user_code" not in st.session_state:
    st.session_state.user_code = ""

# --------------------
# Database Setup (In-Memory)
# --------------------
# Database connection stored in session state for persistence
if 'db_conn' not in st.session_state:
    st.session_state.db_conn = sqlite3.connect(':memory:', check_same_thread=False)
    cursor = st.session_state.db_conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            question_id INTEGER,
            question_title TEXT,
            score INTEGER,
            duration REAL,
            passed_tests INTEGER,
            total_tests INTEGER,
            created_at TEXT
        )
    """)
    st.session_state.db_conn.commit()

def save_progress(username, q_id, title, passed, total, duration, score):
    try:
        cursor = st.session_state.db_conn.cursor()
        cursor.execute("""
            INSERT INTO progress (username, question_id, question_title, score, duration, passed_tests, total_tests, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (username, q_id, title, score, duration, passed, total, datetime.now().isoformat()))
        st.session_state.db_conn.commit()
    except Exception as e:
        st.warning(f"Could not save progress: {e}")

def load_leaderboard():
    df = None
    try:
        import pandas as pd
        df = pd.read_sql_query("""
            SELECT username, SUM(score) AS total_score, COUNT(*) AS challenges_completed, 
                   ROUND(SUM(duration), 2) AS total_time
            FROM progress
            GROUP BY username
            ORDER BY total_score DESC, total_time ASC
        """, st.session_state.db_conn)
    except Exception as e:
        pass  # Silently fail if no data yet
    return df

# --------------------
# Load Questions (local)
# --------------------
def get_questions():
    return [
        {
            "id": 1,
            "title": "Sum Two Numbers",
            "difficulty": "Easy",
            "desc": "Write a function that takes two integers and returns their sum.",
            "starter": "def add_numbers(a, b):\n    # TODO\n    pass",
            "tests": [
                {"input": {"a": 2, "b": 3}, "expected": 5},
                {"input": {"a": -1, "b": 1}, "expected": 0},
            ],
            "solution": "def add_numbers(a,b): return a+b",
        },
        {
            "id": 2,
            "title": "Find Maximum",
            "difficulty": "Easy",
            "desc": "Return the maximum number in a list.",
            "starter": "def find_max(nums):\n    # TODO\n    pass",
            "tests": [
                {"input": {"nums": [1,2,3]}, "expected": 3},
                {"input": {"nums": [-5,0,5]}, "expected": 5},
            ],
            "solution": "def find_max(nums): return max(nums)",
        },
        {
            "id": 3,
            "title": "Check Palindrome",
            "difficulty": "Medium",
            "desc": "Return True if a given string is a palindrome.",
            "starter": "def is_palindrome(s):\n    # TODO\n    pass",
            "tests": [
                {"input": {"s": "racecar"}, "expected": True},
                {"input": {"s": "hello"}, "expected": False},
            ],
            "solution": "def is_palindrome(s): return s == s[::-1]",
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
            func = list(local_vars.values())[0]
            output = func(**case["input"])
            passed = output == case["expected"]
            results.append({"passed": passed, "input": case["input"], "expected": case["expected"], "actual": output})
        except Exception as e:
            results.append({"passed": False, "error": str(e)})
    return results

# --------------------
# UI
# --------------------
st.title(f"🏁 Progressive Coding Challenge")

# Progress indicator
progress_val = st.session_state.current_q_index / total_questions
st.progress(progress_val, text=f"Challenge {st.session_state.current_q_index + 1} of {total_questions}")

current = questions[st.session_state.current_q_index]
st.subheader(f"📘 {current['title']} ({current['difficulty']})")
st.write(current["desc"])
st.divider()

# Code editor
user_code = st.text_area("Write your code here:", value=current["starter"], height=200, key=f"code_{st.session_state.current_q_index}")

# Buttons
col1, col2 = st.columns(2)
with col1:
    run_btn = st.button("▶️ Run Tests", use_container_width=True)
with col2:
    next_btn = st.button("➡️ Next Challenge", use_container_width=True, disabled=st.session_state.current_q_index >= total_questions - 1)

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

    if passed == total:
        st.success(f"✅ All tests passed! You scored {score}. Moving to next challenge.")
        save_progress(st.session_state.username, current["id"], current["title"], passed, total, duration, score)
        if st.session_state.current_q_index < total_questions - 1:
            st.session_state.current_q_index += 1
            st.rerun()
        else:
            st.balloons()
            st.success("🎉 You’ve completed all challenges!")
    else:
        st.warning(f"Partial success: {passed}/{total} tests passed.")

# Show results
if st.session_state.test_results:
    st.markdown("### 🧪 Test Results")
    for i, r in enumerate(st.session_state.test_results, 1):
        if r.get("passed", False):
            st.success(f"Test {i} passed ✅ | Input: {r['input']}")
        else:
            error_msg = r.get('error', 'Expected: {} Got: {}'.format(r.get('expected'), r.get('actual')))
            st.error(f"Test {i} failed ❌ | {error_msg}")

# Leaderboard
st.divider()
st.subheader("🏆 Leaderboard")
df = load_leaderboard()
if df is not None and not df.empty:
    st.dataframe(df, use_container_width=True)
else:
    st.info("Leaderboard will appear after some completions.")

# Footer
st.markdown("<br><center>⚡ Built for skill progression & confidence growth.</center>", unsafe_allow_html=True)
st.caption("Note: Progress is stored in memory and will reset when you refresh the page.")