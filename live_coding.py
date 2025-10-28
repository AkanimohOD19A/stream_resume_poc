import streamlit as st
import sqlite3
import time
from datetime import datetime, timedelta
import subprocess
import sys
import io
from contextlib import redirect_stdout, redirect_stderr
from groq import Groq
import json

# Page config
st.set_page_config(
    page_title="Live Coding Interview",
    page_icon="💻",
    layout="wide"
)

# Initialize session state
if 'db_initialized' not in st.session_state:
    st.session_state.db_initialized = False
if 'current_question' not in st.session_state:
    st.session_state.current_question = None
if 'timer_start' not in st.session_state:
    st.session_state.timer_start = None
if 'timer_active' not in st.session_state:
    st.session_state.timer_active = False
if 'code_output' not in st.session_state:
    st.session_state.code_output = ""
if 'test_results' not in st.session_state:
    st.session_state.test_results = []
if 'user_code' not in st.session_state:
    st.session_state.user_code = ""
if 'use_remote_db' not in st.session_state:
    st.session_state.use_remote_db = False

# Database functions
def get_db_connection(turso_url=None, turso_token=None):
    """Get database connection - local SQLite or remote Turso"""
    if turso_url and turso_token and st.session_state.use_remote_db:
        try:
            from libsql_experimental import dbapi2 as libsql
            conn = libsql.connect(database=turso_url, auth_token=turso_token)
            return conn
        except Exception as e:
            st.error(f"Turso connection error: {e}")
            # Fallback to local
            return sqlite3.connect('coding_questions.db')
    else:
        return sqlite3.connect('coding_questions.db')

def init_database(turso_url=None, turso_token=None):
    """Initialize database with coding questions"""
    conn = get_db_connection(turso_url, turso_token)
    cursor = conn.cursor()

    # Create table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            starter_code TEXT,
            test_cases TEXT,
            solution TEXT,
            time_complexity TEXT,
            space_complexity TEXT
        )
    ''')

    # Check if table is empty
    cursor.execute('SELECT COUNT(*) FROM questions')
    if cursor.fetchone()[0] == 0:
        # Insert sample questions
        sample_questions = [
            (
                "Two Sum",
                "Easy",
                "Arrays",
                "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target. You may assume that each input would have exactly one solution, and you may not use the same element twice.",
                "def two_sum(nums, target):\n    # Write your code here\n    pass",
                '[{"input": {"nums": [2,7,11,15], "target": 9}, "expected": [0,1]}, {"input": {"nums": [3,2,4], "target": 6}, "expected": [1,2]}, {"input": {"nums": [3,3], "target": 6}, "expected": [0,1]}]',
                "def two_sum(nums, target):\n    seen = {}\n    for i, num in enumerate(nums):\n        complement = target - num\n        if complement in seen:\n            return [seen[complement], i]\n        seen[num] = i\n    return []",
                "O(n)",
                "O(n)"
            ),
            (
                "Reverse String",
                "Easy",
                "Strings",
                "Write a function that reverses a string. The input string is given as an array of characters s. You must do this by modifying the input array in-place with O(1) extra memory.",
                "def reverse_string(s):\n    # Write your code here\n    pass",
                '[{"input": {"s": ["h","e","l","l","o"]}, "expected": ["o","l","l","e","h"]}, {"input": {"s": ["H","a","n","n","a","h"]}, "expected": ["h","a","n","n","a","H"]}]',
                "def reverse_string(s):\n    left, right = 0, len(s) - 1\n    while left < right:\n        s[left], s[right] = s[right], s[left]\n        left += 1\n        right -= 1",
                "O(n)",
                "O(1)"
            ),
            (
                "Valid Palindrome",
                "Easy",
                "Strings",
                "A phrase is a palindrome if, after converting all uppercase letters into lowercase letters and removing all non-alphanumeric characters, it reads the same forward and backward. Given a string s, return true if it is a palindrome, or false otherwise.",
                "def is_palindrome(s):\n    # Write your code here\n    pass",
                '[{"input": {"s": "A man, a plan, a canal: Panama"}, "expected": true}, {"input": {"s": "race a car"}, "expected": false}, {"input": {"s": " "}, "expected": true}]',
                "def is_palindrome(s):\n    cleaned = ''.join(c.lower() for c in s if c.isalnum())\n    return cleaned == cleaned[::-1]",
                "O(n)",
                "O(n)"
            ),
            (
                "Fibonacci Number",
                "Easy",
                "Dynamic Programming",
                "The Fibonacci numbers, commonly denoted F(n) form a sequence, such that each number is the sum of the two preceding ones, starting from 0 and 1. Given n, calculate F(n).",
                "def fibonacci(n):\n    # Write your code here\n    pass",
                '[{"input": {"n": 2}, "expected": 1}, {"input": {"n": 3}, "expected": 2}, {"input": {"n": 4}, "expected": 3}, {"input": {"n": 10}, "expected": 55}]',
                "def fibonacci(n):\n    if n <= 1:\n        return n\n    a, b = 0, 1\n    for _ in range(2, n + 1):\n        a, b = b, a + b\n    return b",
                "O(n)",
                "O(1)"
            ),
            (
                "Binary Search",
                "Medium",
                "Binary Search",
                "Given an array of integers nums which is sorted in ascending order, and an integer target, write a function to search target in nums. If target exists, then return its index. Otherwise, return -1.",
                "def binary_search(nums, target):\n    # Write your code here\n    pass",
                '[{"input": {"nums": [-1,0,3,5,9,12], "target": 9}, "expected": 4}, {"input": {"nums": [-1,0,3,5,9,12], "target": 2}, "expected": -1}]',
                "def binary_search(nums, target):\n    left, right = 0, len(nums) - 1\n    while left <= right:\n        mid = (left + right) // 2\n        if nums[mid] == target:\n            return mid\n        elif nums[mid] < target:\n            left = mid + 1\n        else:\n            right = mid - 1\n    return -1",
                "O(log n)",
                "O(1)"
            )
        ]

        cursor.executemany('''
            INSERT INTO questions (title, difficulty, category, description, starter_code, test_cases, solution, time_complexity, space_complexity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_questions)

        conn.commit()

    conn.close()
    st.session_state.db_initialized = True

def get_all_questions(turso_url=None, turso_token=None):
    """Retrieve all questions from database"""
    conn = get_db_connection(turso_url, turso_token)
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, difficulty, category FROM questions')
    questions = cursor.fetchall()
    conn.close()
    return questions

def get_question_by_id(question_id, turso_url=None, turso_token=None):
    """Retrieve specific question by ID"""
    conn = get_db_connection(turso_url, turso_token)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM questions WHERE id = ?', (question_id,))
    question = cursor.fetchone()
    conn.close()
    return question


def run_python_code(code, test_cases):
    """Execute Python code with test cases"""
    results = []

    for idx, test in enumerate(test_cases):
        try:
            # Create a safe execution environment
            local_vars = {}
            global_vars = {'__builtins__': __builtins__}

            # Execute the user's code
            exec(code, global_vars, local_vars)

            # Get the function name (assume first function defined)
            func_name = None
            for key, value in local_vars.items():
                if callable(value):
                    func_name = key
                    break

            if not func_name:
                results.append({
                    'test_num': idx + 1,
                    'passed': False,
                    'error': 'No function found in code'
                })
                continue

            # Run the test
            func = local_vars[func_name]
            input_data = test['input']
            expected = test['expected']

            # Call function with unpacked arguments
            if isinstance(input_data, dict):
                actual = func(**input_data)
            else:
                actual = func(input_data)

            # Compare results
            passed = actual == expected
            results.append({
                'test_num': idx + 1,
                'passed': passed,
                'input': input_data,
                'expected': expected,
                'actual': actual,
                'error': None
            })

        except Exception as e:
            results.append({
                'test_num': idx + 1,
                'passed': False,
                'error': str(e)
            })

    return results


def assess_code_with_ai(question_desc, user_code, test_results, api_key):
    """Use Groq AI to assess the code quality and approach"""
    passed_tests = sum(1 for r in test_results if r['passed'])
    total_tests = len(test_results)

    prompt = f"""You are an expert coding interviewer. Assess the following coding solution:

Question: {question_desc}

Candidate's Code:
```python
{user_code}
```

Test Results: {passed_tests}/{total_tests} tests passed

Provide assessment in JSON format:
{{
    "correctness_score": <1-10>,
    "code_quality_score": <1-10>,
    "efficiency_score": <1-10>,
    "overall_score": <1-10>,
    "strengths": ["..."],
    "weaknesses": ["..."],
    "suggestions": ["..."],
    "verdict": "Pass/Fail/Borderline"
}}

Focus on: correctness, code quality, time/space complexity, edge cases, readability.
"""

    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
            temperature=0.3
        )

        result = response.choices[0].message.content
        # Extract JSON
        json_start = result.find('{')
        json_end = result.rfind('}') + 1
        json_str = result[json_start:json_end]
        return json.loads(json_str)
    except Exception as e:
        st.error(f"Error in AI assessment: {e}")
        return None

# Timer functions
def start_timer():
    """Start the 30-minute timer"""
    st.session_state.timer_start = datetime.now()
    st.session_state.timer_active = True


def get_remaining_time():
    """Get remaining time in seconds"""
    if not st.session_state.timer_active or not st.session_state.timer_start:
        return 1800  # 30 minutes

    elapsed = (datetime.now() - st.session_state.timer_start).total_seconds()
    remaining = max(0, 1800 - elapsed)
    return remaining


def format_time(seconds):
    """Format seconds to MM:SS"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"

# Initialize database
turso_url = None
turso_token = None

if not st.session_state.db_initialized:
    # Check for Turso credentials in sidebar
    if 'turso_url' in st.session_state and 'turso_token' in st.session_state:
        turso_url = st.session_state.turso_url
        turso_token = st.session_state.turso_token
        if turso_url and turso_token:
            st.session_state.use_remote_db = True

    init_database(turso_url, turso_token)

# Main UI
st.title("💻 Live Coding Interview")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")

    # Database Configuration
    st.subheader("💾 Database")
    db_option = st.radio("Database Type:", ["Local SQLite", "Remote Turso"])

    if db_option == "Remote Turso":
        turso_url = st.text_input("Turso Database URL", placeholder="libsql://your-db.turso.io")
        turso_token = st.text_input("Turso Auth Token", type="password")

        if turso_url and turso_token:
            st.session_state.turso_url = turso_url
            st.session_state.turso_token = turso_token
            st.session_state.use_remote_db = True
            st.success("✅ Using Turso (Remote)")
        else:
            st.warning("⚠️ Enter Turso credentials")
    else:
        st.session_state.use_remote_db = False
        st.info("📁 Using Local SQLite")
        turso_url = None
        turso_token = None

    st.markdown("---")

    groq_api_key = st.text_input("Groq API Key", type="password")

    st.markdown("---")
    st.header("📝 Question Bank")

    questions = get_all_questions(turso_url, turso_token)

    if questions:
        question_options = {f"{q[1]} ({q[2]}) - {q[3]}": q[0] for q in questions}
        selected = st.selectbox("Select a question:", list(question_options.keys()))

        if st.button("Load Question", type="primary"):
            question_id = question_options[selected]
            st.session_state.current_question = get_question_by_id(question_id, turso_url, turso_token)
            st.session_state.user_code = st.session_state.current_question[5]  # starter code
            st.session_state.timer_start = None
            st.session_state.timer_active = False
            st.session_state.test_results = []
            st.rerun()

    st.markdown("---")
    st.header("⏱️ Timer")

    if not st.session_state.timer_active:
        if st.button("▶️ Start 30-Min Timer"):
            start_timer()
            st.rerun()
    else:
        remaining = get_remaining_time()
        if remaining > 0:
            st.info(f"⏱️ Time Remaining: **{format_time(remaining)}**")
            if remaining < 300:  # Less than 5 minutes
                st.warning("⚠️ Less than 5 minutes remaining!")
        else:
            st.error("⏰ Time's Up!")

# Check if API key is provided
if not groq_api_key:
    st.warning("⚠️ Please enter your Groq API key in the sidebar")
    st.stop()

# Check if question is loaded
if not st.session_state.current_question:
    st.info("👈 Please select and load a question from the sidebar to begin")
    st.stop()

# Get current question details
q = st.session_state.current_question
question_id, title, difficulty, category, description, starter_code, test_cases_json, solution, time_comp, space_comp = q

# Display question info
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.subheader(f"📌 {title}")
with col2:
    difficulty_colors = {"Easy": "🟢", "Medium": "🟡", "Hard": "🔴"}
    st.markdown(f"**{difficulty_colors.get(difficulty, '⚪')} {difficulty}**")
with col3:
    st.markdown(f"**Category:** {category}")

st.markdown("---")

# Main layout: 2 columns
left_col, right_col = st.columns([1, 1])

with left_col:
    st.subheader("📝 Problem Description")
    st.markdown(description)

    st.markdown("---")

    st.subheader("📊 Constraints & Complexity")
    col_a, col_b = st.columns(2)
    with col_a:
        st.info(f"**Time:** {time_comp}")
    with col_b:
        st.info(f"**Space:** {space_comp}")

    st.markdown("---")

    # Test cases preview
    with st.expander("🧪 View Test Cases"):
        test_cases = json.loads(test_cases_json)
        for idx, test in enumerate(test_cases, 1):
            st.markdown(f"**Test {idx}:**")
            st.code(json.dumps(test, indent=2), language="json")

with right_col:
    st.subheader("💻 Code Editor")

    # Add Ace Editor with proper indentation support
    st.markdown("""
    <style>
    #ace-editor {
        width: 100%;
        height: 400px;
        border: 1px solid #ddd;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Try to use streamlit-ace if available, otherwise fallback to enhanced text_area
    try:
        from streamlit_ace import st_ace

        user_code = st_ace(
            value=st.session_state.user_code,
            language='python',
            theme='monokai',
            keybinding='vscode',
            font_size=14,
            tab_size=4,
            show_gutter=True,
            show_print_margin=False,
            wrap=False,
            auto_update=True,
            readonly=False,
            min_lines=20,
            key="ace_editor",
            height=400
        )
    except ImportError:
        # Fallback: Enhanced text area with JavaScript for Tab key
        st.markdown("""
        <script>
        document.addEventListener('DOMContentLoaded', function() {
            const textareas = document.querySelectorAll('textarea');
            textareas.forEach(textarea => {
                textarea.addEventListener('keydown', function(e) {
                    if (e.key === 'Tab') {
                        e.preventDefault();
                        const start = this.selectionStart;
                        const end = this.selectionEnd;
                        const value = this.value;
                        this.value = value.substring(0, start) + '    ' + value.substring(end);
                        this.selectionStart = this.selectionEnd = start + 4;
                    }
                });
            });
        });
        </script>
        """, unsafe_allow_html=True)

        user_code = st.text_area(
            "Write your solution here (Press Tab for 4 spaces):",
            value=st.session_state.user_code,
            height=400,
            key="code_editor",
            help="Tip: Press Tab key to insert 4 spaces for proper Python indentation"
        )

        # Add indentation helper buttons
        col_indent1, col_indent2 = st.columns(2)
        with col_indent1:
            if st.button("➡️ Indent Line", help="Add 4 spaces to start of line"):
                lines = user_code.split('\n')
                if lines:
                    lines = ['    ' + line for line in lines]
                    st.session_state.user_code = '\n'.join(lines)
                    st.rerun()
        with col_indent2:
            if st.button("⬅️ Unindent Line", help="Remove 4 spaces from start"):
                lines = user_code.split('\n')
                if lines:
                    lines = [line[4:] if line.startswith('    ') else line for line in lines]
                    st.session_state.user_code = '\n'.join(lines)
                    st.rerun()

    # Action buttons
    btn_col1, btn_col2 = st.columns(2)

    with btn_col1:
        if st.button("▶️ Run Tests", type="primary", use_container_width=True):
            if user_code.strip():
                with st.spinner("Running tests..."):
                    test_cases = json.loads(test_cases_json)
                    results = run_python_code(user_code, test_cases)
                    st.session_state.test_results = results
                    st.session_state.user_code = user_code
                    st.rerun()
            else:
                st.error("Please write some code first!")

    with btn_col2:
        if st.button("🤖 AI Assessment", use_container_width=True):
            if st.session_state.test_results:
                with st.spinner("AI is reviewing your code..."):
                    assessment = assess_code_with_ai(
                        description,
                        user_code,
                        st.session_state.test_results,
                        groq_api_key
                    )
                    if assessment:
                        st.session_state.ai_assessment = assessment
                        st.rerun()
            else:
                st.warning("Please run tests first!")

# Display test results
if st.session_state.test_results:
    st.markdown("---")
    st.subheader("🧪 Test Results")

    passed = sum(1 for r in st.session_state.test_results if r['passed'])
    total = len(st.session_state.test_results)

    progress = passed / total if total > 0 else 0
    st.progress(progress, text=f"Passed: {passed}/{total} tests")

    for result in st.session_state.test_results:
        with st.expander(
            f"Test {result['test_num']}: {'✅ PASSED' if result['passed'] else '❌ FAILED'}",
            expanded=not result['passed']
        ):
            if result['passed']:
                st.success("Test passed!")
                if 'input' in result:
                    st.code(f"Input: {result['input']}\nExpected: {result['expected']}\nActual: {result['actual']}")
            else:
                st.error(f"Error: {result.get('error', 'Output mismatch')}")
                if 'input' in result:
                    st.code(f"Input: {result.get('input', 'N/A')}\nExpected: {result.get('expected', 'N/A')}\nActual: {result.get('actual', 'N/A')}")

# Display AI assessment
if 'ai_assessment' in st.session_state:
    st.markdown("---")
    st.subheader("🤖 AI Code Assessment")

    assessment = st.session_state.ai_assessment

    # Scores
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Correctness", f"{assessment.get('correctness_score', 0)}/10")
    with col2:
        st.metric("Code Quality", f"{assessment.get('code_quality_score', 0)}/10")
    with col3:
        st.metric("Efficiency", f"{assessment.get('efficiency_score', 0)}/10")
    with col4:
        overall = assessment.get('overall_score', 0)
        st.metric("Overall", f"{overall}/10")

    # Verdict
    verdict = assessment.get('verdict', 'Unknown')
    verdict_colors = {
        'Pass': '🟢',
        'Fail': '🔴',
        'Borderline': '🟡'
    }
    st.markdown(f"### {verdict_colors.get(verdict, '⚪')} Verdict: **{verdict}**")

    # Detailed feedback
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("**✅ Strengths:**")
        for strength in assessment.get('strengths', []):
            st.markdown(f"- {strength}")

    with col_b:
        st.markdown("**⚠️ Weaknesses:**")
        for weakness in assessment.get('weaknesses', []):
            st.markdown(f"- {weakness}")

    st.markdown("**💡 Suggestions for Improvement:**")
    for suggestion in assessment.get('suggestions', []):
        st.markdown(f"- {suggestion}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>Live Coding Interview | Powered by Groq AI</p>
</div>
""", unsafe_allow_html=True)

# Auto-refresh timer every second
if st.session_state.timer_active:
    time.sleep(1)
    st.rerun()