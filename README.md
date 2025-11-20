### Calibration Test

**Description**

This uploads your resume (and optionally a job description) → 
    the system infers your strongest coding skills → 
        generates a short calibration quiz/test → 
            scores you → unlocks a personalized challenge path.

[Skill Calibration App]
  └─ Resume Upload
    └─ AI Strength Analysis
          └─ Calibration Quiz
              └─ Skill Path Recommendation
                    ↓
[Progressive Challenge App]
  └─ Timed Tasks → Scoring → Leaderboard

**Flow Chart**

Resume/Job Description Upload
      ↓
Skill Extraction & Strength Profiling (AI or keyword-based)
      ↓
Calibration Test (timed micro-challenges, scored)
      ↓
Path Recommendation (e.g., Python Intermediate → start with 5-min tasks)

##
# 🏗️ App Structure & Setup Guide

## 📁 Recommended File Structure

```
your-project/
├── .streamlit/
│   └── secrets.toml              # Supabase credentials
│
├── pages/                        # Streamlit multi-page app
│   ├── 1_🏁_Challenges.py       # Main coding challenge page
│   ├── 2_📊_My_Progress.py      # User progress page
│   └── 3_⚙️_Admin.py            # Question management (optional)
│
├── Home.py                       # Landing/calibration page
├── requirements.txt              # Dependencies
└── README.md
```

## 🚀 Quick Setup

### 1. Create the Files

**Home.py** (Landing page - use the Calibration artifact)
```python
# Copy the Calibration/Login Page artifact code here
```

**pages/1_🏁_Challenges.py** (Main app - use the REST Coding Challenge artifact)
```python
# Copy the REST-Only Coding Challenge App artifact code here
```

### 2. Install Dependencies

**requirements.txt**
```txt
streamlit>=1.28.0
streamlit-monaco-editor>=0.1.0
requests>=2.31.0
```

Install:
```bash
pip install -r requirements.txt
```

### 3. Configure Secrets

**.streamlit/secrets.toml**
```toml
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-anon-key-here"
```

### 4. Run the App

```bash
streamlit run Home.py
```

The app will automatically create navigation with:
- **Home** - Login/calibration page
- **🏁 Challenges** - Main coding challenges
- **📊 My Progress** - User stats (optional)
- **⚙️ Admin** - Question management (optional)

---

## 📄 Complete File Templates

### File: `Home.py`

```python
import streamlit as st

st.set_page_config(
    page_title="Welcome to Coding Challenges",
    page_icon="🎯",
    layout="centered"
)

st.markdown('<div style="font-size: 3rem; font-weight: bold; text-align: center;">🏁 Coding Challenges</div>', unsafe_allow_html=True)
st.markdown('<div style="font-size: 1.2rem; text-align: center; color: #666; margin-bottom: 2rem;">Master Python through progressive challenges</div>', unsafe_allow_html=True)

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
st.markdown("### 👤 Enter Your Username")

username = st.text_input(
    "Username",
    placeholder="Enter a unique username",
    max_chars=50,
    help="Choose a username to track your progress"
)

if st.button("🚀 Start Coding", type="primary", use_container_width=True):
    if username and username.strip():
        st.session_state.username = username.strip()
        st.success(f"Welcome, {username}! 🎉")
        st.info("👉 Navigate to '🏁 Challenges' page to start coding!")
    else:
        st.error("Please enter a valid username")

# Show current user
if st.session_state.get("username"):
    st.sidebar.success(f"👤 Logged in as: **{st.session_state.username}**")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.username = None
        st.rerun()
```

---

### File: `pages/1_🏁_Challenges.py`

Copy the entire **REST-Only Coding Challenge App** artifact code here.

---

### File: `pages/2_📊_My_Progress.py` (Optional)

```python
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
```

---

## 🎨 Customization Tips

### Change Theme

Create `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#262730"
textColor = "#FAFAFA"
font = "sans serif"
```

### Add Custom Logo

```python
from PIL import Image
logo = Image.open("logo.png")
st.sidebar.image(logo, use_column_width=True)
```

### Add Analytics

```python
# Track page views
if "page_views" not in st.session_state:
    st.session_state.page_views = 0
st.session_state.page_views += 1
```

---

## 🚀 Deployment

### Deploy to Streamlit Cloud

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app"
4. Select your repo and branch
5. Set main file path: `Home.py`
6. Add secrets in "Advanced settings"
7. Deploy!

### Add Secrets in Streamlit Cloud

In app settings, add:
```toml
SUPABASE_URL = "https://xxxxx.supabase.co"
SUPABASE_KEY = "your-anon-key"
```

---

## ✅ Testing Checklist

Before deploying:
- [ ] Test username login
- [ ] Verify questions load
- [ ] Submit a solution
- [ ] Check progress saves
- [ ] View leaderboard
- [ ] Test navigation between pages
- [ ] Verify on mobile
- [ ] Check error handling

---

## 🎯 Next Steps

1. **Add more challenges** - Use the SQL schema to add questions
2. **Create user profiles** - Show badges and achievements
3. **Add difficulty filters** - Let users filter by Easy/Medium/Hard
4. **Implement timer** - Add countdown for timed challenges
5. **Add hints system** - Deduct points for using hints
6. **Premium features** - Gate advanced challenges behind premium tier

---

## 📚 Resources

- [Streamlit Multi-Page Apps](https://docs.streamlit.io/library/get-started/multipage-apps)
- [Supabase REST API](https://supabase.com/docs/guides/api)
- [Streamlit Deployment](https://docs.streamlit.io/streamlit-community-cloud/get-started)

Need help? Check the other artifacts or ask for specific features!