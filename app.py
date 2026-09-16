import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import time
import html
import json
import re
from datetime import datetime
from supabase import create_client, Client

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Pro Quiz Portal | Enterprise Edition",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- ENTERPRISE THEME, CUSTOM FONTS & MODERN CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    /* Global Base Styling */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #0f172a;
    }

    /* Dynamic Modern Mesh Gradient Background */
    .stApp {
        background-color: #f8fafc;
        background-image: 
            radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.08) 0px, transparent 50%),
            radial-gradient(at 100% 0%, rgba(139, 92, 246, 0.07) 0px, transparent 50%),
            radial-gradient(at 50% 100%, rgba(59, 130, 246, 0.06) 0px, transparent 50%);
        background-attachment: fixed;
    }

    /* Headings */
    h1, h2, h3, h4 {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
        color: #0f172a;
    }

    /* Enterprise Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4338ca 100%);
        border-radius: 20px;
        padding: 32px 28px;
        color: white;
        text-align: center;
        margin-bottom: 28px;
        box-shadow: 0 20px 25px -5px rgba(49, 46, 129, 0.2), 0 8px 10px -6px rgba(49, 46, 129, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.12);
        position: relative;
        overflow: hidden;
    }
    .hero-banner::after {
        content: "";
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 60%);
        pointer-events: none;
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0;
        color: #ffffff !important;
    }
    .hero-subtitle {
        font-size: 0.95rem;
        color: #c7d2fe;
        margin-top: 6px;
        font-weight: 400;
    }

    /* Question Box */
    .question-box {
        background: #ffffff;
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
        margin-bottom: 22px;
        border: 1px solid #e2e8f0;
        border-left: 6px solid #4f46e5;
        transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .question-box:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 20px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -4px rgba(0, 0, 0, 0.03);
    }

    .question-text-content {
        font-size: 1.05rem;
        font-weight: 600;
        color: #1e293b;
        white-space: pre-wrap;
        word-break: break-word;
        margin-bottom: 12px;
        line-height: 1.6;
    }

    /* Warning Card */
    .warning-card {
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
        border: 1.5px solid #ef4444;
        border-radius: 14px;
        padding: 16px 20px;
        margin-bottom: 20px;
        color: #991b1b;
        box-shadow: 0 4px 6px -1px rgba(239, 68, 68, 0.1);
    }

    /* Review Card Variations */
    .review-box {
        background: #ffffff;
        padding: 22px 24px;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04);
        margin-bottom: 20px;
        border: 1px solid #e2e8f0;
        transition: transform 0.15s ease;
    }
    .review-box-correct {
        border-left: 6px solid #10b981;
        background: linear-gradient(to right, #f0fdf4 0%, #ffffff 15%);
    }
    .review-box-wrong {
        border-left: 6px solid #ef4444;
        background: linear-gradient(to right, #fef2f2 0%, #ffffff 15%);
    }
    .review-box-skipped {
        border-left: 6px solid #94a3b8;
        background: linear-gradient(to right, #f8fafc 0%, #ffffff 15%);
    }

    /* Badges & Pills */
    .badge-mark {
        display: inline-block;
        background: #eef2ff;
        color: #4338ca;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.03em;
        text-transform: uppercase;
        border: 1px solid #c7d2fe;
        margin-left: 6px;
        vertical-align: middle;
    }
    .badge-neg {
        display: inline-block;
        background: #fef2f2;
        color: #b91c1c;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        border: 1px solid #fecaca;
        margin-left: 4px;
        vertical-align: middle;
    }
    .badge-correct {
        display: inline-block;
        background: #dcfce7;
        color: #15803d;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 700;
        border: 1px solid #bbf7d0;
        margin-left: 6px;
        vertical-align: middle;
    }
    .badge-wrong {
        display: inline-block;
        background: #fee2e2;
        color: #b91c1c;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 700;
        border: 1px solid #fecaca;
        margin-left: 6px;
        vertical-align: middle;
    }
    .badge-unattempted {
        display: inline-block;
        background: #f1f5f9;
        color: #64748b;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 600;
        border: 1px solid #cbd5e1;
        margin-left: 6px;
        vertical-align: middle;
    }

    /* Option Review Rows */
    .option-item {
        padding: 10px 14px;
        border-radius: 10px;
        margin-bottom: 8px;
        font-size: 0.95rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border: 1px solid #e2e8f0;
    }
    .option-default {
        background-color: #f8fafc;
        color: #334155;
    }
    .option-correct-key {
        background-color: #f0fdf4;
        border-color: #86efac;
        color: #166534;
        font-weight: 600;
    }
    .option-user-wrong {
        background-color: #fef2f2;
        border-color: #fca5a5;
        color: #991b1b;
        font-weight: 600;
    }

    /* Primary Buttons */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.25) !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 18px rgba(79, 70, 229, 0.35) !important;
    }
</style>
""", unsafe_allow_html=True)

# --- SUPABASE CREDENTIALS DIRECT SETUP ---
SUPABASE_URL = "https://jbayaagktyvesjwwbeha.supabase.co"
SUPABASE_KEY = "sb_publishable_8PbBG3BVlMXTt5bIzY9HpQ_2h1YNAYt"


@st.cache_resource
def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)


supabase = get_supabase_client()


# --- INTELLIGENT COURSE & SEMESTER NORMALIZATION HELPER ---
def normalize_course_name(raw_text: str, existing_branches: list = None) -> str:
    """
    Normalizes any format of course & semester into a single unified standard.
    Example: 'Btech 5th sem', 'BTECH 5th Semester', 'B.Tech 5th sem' -> 'BTECH 5th Semester'
    """
    if not raw_text:
        return ""
    text = str(raw_text).strip()

    def make_key(s):
        s = s.lower()
        s = re.sub(r'[^a-z0-9]', '', s)
        s = s.replace('semester', 'sem')
        s = s.replace('first', '1st').replace('second', '2nd').replace('third', '3rd')
        s = s.replace('fourth', '4th').replace('fifth', '5th').replace('sixth', '6th')
        s = s.replace('seventh', '7th').replace('eighth', '8th')
        s = re.sub(r'(\d)(sem)', r'\1th\2', s)
        return s

    target_key = make_key(text)

    # Match with existing branches in the database if available
    if existing_branches:
        for b in existing_branches:
            if make_key(b) == target_key:
                return b

    # Standardize common course degree acronyms
    s = re.sub(r'(?i)\bb\s*\.?\s*tech\b', 'BTECH', text)
    s = re.sub(r'(?i)\bm\s*\.?\s*tech\b', 'MTECH', s)
    s = re.sub(r'(?i)\bb\s*\.?\s*c\s*\.?\s*a\b', 'BCA', s)
    s = re.sub(r'(?i)\bm\s*\.?\s*c\s*\.?\s*a\b', 'MCA', s)
    s = re.sub(r'(?i)\bb\s*\.?\s*s\s*\.?\s*c\b', 'BSC', s)
    s = re.sub(r'(?i)\bm\s*\.?\s*s\s*\.?\s*c\b', 'MSC', s)
    s = re.sub(r'(?i)\bb\s*\.?\s*b\s*\.?\s*a\b', 'BBA', s)
    s = re.sub(r'(?i)\bm\s*\.?\s*b\s*\.?\s*a\b', 'MBA', s)
    s = re.sub(r'(?i)\bb\s*\.?\s*e\b', 'BE', s)
    s = re.sub(r'(?i)\bm\s*\.?\s*e\b', 'ME', s)

    cleaned = re.sub(r'[\.\-_]', ' ', s)
    tokens = [t.strip() for t in cleaned.split() if t.strip()]

    course_parts = []
    sem_num = None
    has_sem_word = False

    num_words = {
        '1': '1st', '1st': '1st', 'first': '1st',
        '2': '2nd', '2nd': '2nd', 'second': '2nd',
        '3': '3rd', '3rd': '3rd', 'third': '3rd',
        '4': '4th', '4th': '4th', 'fourth': '4th',
        '5': '5th', '5th': '5th', 'fifth': '5th',
        '6': '6th', '6th': '6th', 'sixth': '6th',
        '7': '7th', '7th': '7th', 'seventh': '7th',
        '8': '8th', '8th': '8th', 'eighth': '8th',
    }

    for token in tokens:
        tl = token.lower()
        if tl in ['sem', 'semester', 'semesters']:
            has_sem_word = True
        elif tl in num_words:
            sem_num = num_words[tl]
        elif re.match(r'^[1-8](st|nd|rd|th)?$', tl):
            digit = tl[0]
            sem_num = num_words.get(digit, f'{digit}th')
        else:
            m = re.match(r'^([1-8])(st|nd|rd|th)?(sem|semester)?$', tl)
            if m:
                sem_num = num_words.get(m.group(1), f'{m.group(1)}th')
                has_sem_word = True
            else:
                course_parts.append(token.upper())

    course_str = ' '.join(course_parts)
    if sem_num:
        return f'{course_str} {sem_num} Semester'.strip()
    elif has_sem_word:
        return f'{course_str} Semester'.strip()
    else:
        return course_str if course_str else text


# --- DATABASE HELPER FUNCTIONS ---
def get_all_questions():
    try:
        res = supabase.table("questions").select("*").execute()
        return res.data or []
    except Exception as e:
        st.error(f"Error fetching questions: {e}")
        return []


def get_questions_by_branch(branch):
    try:
        res = supabase.table("questions").select("*").ilike("branch", branch.strip()).execute()
        return res.data or []
    except Exception as e:
        st.error(f"Error fetching branch questions: {e}")
        return []


def add_question(q_data):
    supabase.table("questions").insert(q_data).execute()


def update_question(q_id, q_data):
    supabase.table("questions").update(q_data).eq("id", q_id).execute()


def delete_question(q_id):
    supabase.table("questions").delete().eq("id", q_id).execute()


def get_all_settings():
    try:
        res = supabase.table("settings").select("*").execute()
        return res.data or []
    except Exception:
        return []


def get_branch_settings(branch):
    try:
        res = supabase.table("settings").select("*").ilike("branch", branch.strip()).execute()
        if res.data and len(res.data) > 0:
            return {
                "time_limit": res.data[0].get("time_limit", 30),
                "passkey": str(res.data[0].get("passkey") or "").strip()
            }
    except Exception:
        pass
    return {"time_limit": 30, "passkey": ""}


def save_branch_settings(branch, time_limit, passkey):
    payload = {
        "branch": branch.strip(),
        "time_limit": int(time_limit),
        "passkey": str(passkey).strip()
    }
    supabase.table("settings").upsert(payload).execute()


def get_all_scores():
    try:
        res = supabase.table("scores").select("*").order("score", desc=True).execute()
        return res.data or []
    except Exception as e:
        st.error(f"Error fetching scores: {e}")
        return []


def get_student_score(roll_no):
    try:
        res = supabase.table("scores").select("*").eq("roll_no", roll_no.strip().upper()).execute()
        if res.data and len(res.data) > 0:
            return res.data[0]
    except Exception:
        pass
    return None


def get_branch_scores(branch):
    try:
        res = supabase.table("scores").select("*").ilike("branch", branch.strip()).order("score", desc=True).execute()
        return res.data or []
    except Exception:
        return []


def save_student_score(score_record):
    supabase.table("scores").upsert(score_record).execute()


def delete_student_score(roll_no):
    supabase.table("scores").delete().eq("roll_no", roll_no).execute()


def delete_branch_data(branch):
    supabase.table("questions").delete().ilike("branch", branch.strip()).execute()
    supabase.table("scores").delete().ilike("branch", branch.strip()).execute()
    supabase.table("settings").delete().ilike("branch", branch.strip()).execute()


def wipe_all_data():
    supabase.table("questions").delete().neq("id", -1).execute()
    supabase.table("scores").delete().neq("roll_no", "__none__").execute()
    supabase.table("settings").delete().neq("branch", "__none__").execute()


def parse_saved_responses(responses_data):
    if not responses_data:
        return {}
    if isinstance(responses_data, dict):
        return responses_data
    if isinstance(responses_data, str):
        try:
            return json.loads(responses_data)
        except Exception:
            return {}
    return {}


# --- PERSISTENT SESSION RESTORATION (Prevents logout and timer reset on browser reload) ---
query_params = st.query_params

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    saved_role = query_params.get("session_role")
    saved_user = query_params.get("session_user")
    if saved_role == "admin" and saved_user == "admin":
        st.session_state.logged_in = True
        st.session_state.user_id = "admin"
        st.session_state.role = "admin"
        st.session_state.student_info = {}
    elif saved_role == "candidate" and saved_user:
        st.session_state.logged_in = True
        st.session_state.user_id = saved_user
        st.session_state.role = "candidate"
        st.session_state.student_info = {
            "Name": query_params.get("c_name", "Candidate"),
            "Roll No": saved_user,
            "Section": query_params.get("c_section", ""),
            "Branch": query_params.get("c_branch", "")
        }
    else:
        st.session_state.logged_in = False
        st.session_state.user_id = ""
        st.session_state.role = ""
        st.session_state.student_info = {}

# Restore original start time from query parameters so refreshing does NOT reset the timer
saved_start_time = query_params.get("start_time")
if saved_start_time:
    try:
        st.session_state.start_time = float(saved_start_time)
    except Exception:
        st.session_state.start_time = None
elif "start_time" not in st.session_state:
    st.session_state.start_time = None


def logout():
    st.session_state.logged_in = False
    st.session_state.user_id = ""
    st.session_state.role = ""
    st.session_state.student_info = {}
    st.session_state.start_time = None
    st.query_params.clear()


# --- LOGIN SCREEN ---
def login_screen():
    st.markdown("""
    <div class="hero-banner">
        <div style="font-size: 2.8rem; margin-bottom: 8px;">🎓</div>
        <h1 class="hero-title">Pro Quiz Portal</h1>
        <p class="hero-subtitle">Enterprise Assessment & Examination Engine</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["👨‍🎓 Candidate Access", "🔐 Administrator Portal"])

    # 1. CANDIDATE ACCESS
    with tab1:
        candidate_subtab1, candidate_subtab2 = st.tabs([
            "🚀 Take Assessment", 
            "🔍 View Past Assessment & Solutions"
        ])

        with candidate_subtab1:
            st.markdown(
                "<p style='font-size: 0.95rem; color: #475569; margin-bottom: 12px;'>All fields are mandatory. Enter your student credentials and authorized passkey to begin or resume your examination.</p>",
                unsafe_allow_html=True)
            with st.form("student_login_form"):
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("Full Name", placeholder="e.g. John Doe")
                    rollno = st.text_input("Roll Number", placeholder="e.g. 23BCA042")
                with col2:
                    section = st.text_input("Section", placeholder="e.g. Section A")
                    branch = st.text_input("Course & Semester", placeholder="e.g. BTech 5th Sem")

                student_passkey = st.text_input("🔑 Quiz Passkey (Issued by Instructor)", type="password",
                                                placeholder="Enter authorization passkey")

                st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
                submit_student = st.form_submit_button("🚀 Access Assessment", type="primary", use_container_width=True)

                if submit_student:
                    # Comprehensive validation: check every detail and provide a clear, specific response if any are missing
                    missing_details = []
                    if not name or not name.strip():
                        missing_details.append("Full Name")
                    if not rollno or not rollno.strip():
                        missing_details.append("Roll Number")
                    if not section or not section.strip():
                        missing_details.append("Section")
                    if not branch or not branch.strip():
                        missing_details.append("Course & Semester")
                    if not student_passkey or not student_passkey.strip():
                        missing_details.append("Quiz Passkey")

                    if missing_details:
                        st.error(f"⚠️ Mandatory details missing! Please provide: {', '.join(missing_details)}.")
                    else:
                        # Group course & semester into single standard representation
                        all_qs = get_all_questions()
                        existing_branches = sorted(list(set([q["branch"] for q in all_qs if q.get("branch")])))
                        clean_branch = normalize_course_name(branch, existing_branches)

                        branch_questions = get_questions_by_branch(clean_branch)
                        if not branch_questions:
                            st.error(f"❌ No active quiz found for '{clean_branch}'. Please verify the course and semester name with your instructor.")
                        else:
                            branch_config = get_branch_settings(clean_branch)
                            required_passkey = branch_config.get("passkey", "")
                            existing_score = get_student_score(rollno)

                            if required_passkey and student_passkey.strip() != required_passkey and not existing_score:
                                st.error("❌ Invalid Quiz Passkey. Please verify with your instructor.")
                            else:
                                clean_roll = rollno.strip().upper()
                                clean_name = name.strip()
                                clean_sec = section.strip()

                                st.session_state.logged_in = True
                                st.session_state.role = "candidate"
                                st.session_state.user_id = clean_roll
                                st.session_state.student_info = {
                                    "Name": clean_name,
                                    "Roll No": clean_roll,
                                    "Section": clean_sec,
                                    "Branch": clean_branch
                                }
                                # Save session to query params so browser reload keeps student logged in
                                st.query_params["session_role"] = "candidate"
                                st.query_params["session_user"] = clean_roll
                                st.query_params["c_name"] = clean_name
                                st.query_params["c_section"] = clean_sec
                                st.query_params["c_branch"] = clean_branch

                                if not existing_score:
                                    start_ts = int(time.time())
                                    st.session_state.start_time = start_ts
                                    st.query_params["start_time"] = str(start_ts)
                                    st.query_params["strikes"] = "0"
                                st.rerun()

        with candidate_subtab2:
            st.markdown(
                "<p style='font-size: 0.95rem; color: #475569; margin-bottom: 12px;'>Review your score, submitted questions, and solutions anytime without needing a passkey.</p>",
                unsafe_allow_html=True)
            with st.form("student_history_form"):
                col_h1, col_h2 = st.columns(2)
                with col_h1:
                    hist_roll = st.text_input("Roll Number", placeholder="e.g. 23BCA042", key="hist_roll")
                with col_h2:
                    hist_branch = st.text_input("Course & Semester", placeholder="e.g. BTech 5th Sem", key="hist_branch")

                st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
                submit_history = st.form_submit_button("🔍 Retrieve My Answer Sheet", type="primary", use_container_width=True)

                if submit_history:
                    missing_hist = []
                    if not hist_roll or not hist_roll.strip():
                        missing_hist.append("Roll Number")
                    if not hist_branch or not hist_branch.strip():
                        missing_hist.append("Course & Semester")

                    if missing_hist:
                        st.error(f"⚠️ Mandatory details missing: Please enter {', '.join(missing_hist)}.")
                    else:
                        clean_roll = hist_roll.strip().upper()
                        all_qs = get_all_questions()
                        existing_branches = sorted(list(set([q["branch"] for q in all_qs if q.get("branch")])))
                        clean_branch = normalize_course_name(hist_branch, existing_branches)

                        rec = get_student_score(clean_roll)
                        if not rec:
                            st.error(f"❌ No completed assessment record found for Roll Number '{clean_roll}'.")
                        else:
                            st.session_state.logged_in = True
                            st.session_state.role = "candidate"
                            st.session_state.user_id = clean_roll
                            st.session_state.student_info = {
                                "Name": rec.get("name", "Student"),
                                "Roll No": clean_roll,
                                "Section": rec.get("section", ""),
                                "Branch": clean_branch
                            }
                            st.query_params["session_role"] = "candidate"
                            st.query_params["session_user"] = clean_roll
                            st.query_params["c_name"] = rec.get("name", "Student")
                            st.query_params["c_section"] = rec.get("section", "")
                            st.query_params["c_branch"] = clean_branch
                            st.rerun()

    # 2. ADMIN LOGIN
    with tab2:
        st.markdown(
            "<p style='font-size: 0.95rem; color: #475569; margin-bottom: 12px;'>Authorized instructor and administrator access only.</p>",
            unsafe_allow_html=True)
        with st.form("admin_login_form"):
            username = st.text_input("Admin Username", placeholder="Enter username")
            password = st.text_input("Admin Password", type="password", placeholder="Enter password")

            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
            submit_admin = st.form_submit_button("Authenticate & Log In", type="primary", use_container_width=True)

            if submit_admin:
                if username == "admin" and password == "admin":
                    st.session_state.logged_in = True
                    st.session_state.user_id = "admin"
                    st.session_state.role = "admin"
                    st.query_params["session_role"] = "admin"
                    st.query_params["session_user"] = "admin"
                    st.rerun()
                else:
                    st.error("❌ Invalid administrative credentials.")


# --- ADMIN DASHBOARD ---
def admin_dashboard():
    col1, col2, col3 = st.columns([3, 1.2, 0.8])
    with col1:
        st.markdown("<h2 style='margin:0;'>⚙️ Examination Control Center</h2>", unsafe_allow_html=True)
        st.caption("Manage questions, security passkeys, durations, and student submissions.")
    with col2:
        if st.button("🔄 Refresh Submissions", use_container_width=True):
            st.toast("Updated with latest database records!", icon="🔄")
            time.sleep(0.3)
            st.rerun()
    with col3:
        st.button("🚪 Log Out", on_click=logout, use_container_width=True)

    st.write("---")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Score Analytics",
        "➕ Add Question",
        "✏️ Question Bank",
        "🔐 Passkey & Limits",
        "🗑️ Data Management"
    ])

    questions = get_all_questions()
    existing_branches = sorted(list(set([normalize_course_name(q["branch"]) for q in questions if q.get("branch")])))
    scores_data = get_all_scores()

    # 1. VIEW RESULTS & PERFORMANCE
    with tab1:
        now_str = datetime.now().strftime("%I:%M:%S %p")
        c_head1, c_head2 = st.columns([3, 1])
        with c_head1:
            st.subheader("Student Submissions & Real-Time Analytics")
        with c_head2:
            st.caption(f"⏱️ Refreshed at: `{now_str}`")

        total_subs = len(scores_data)
        avg_score = (sum(float(s.get("score", 0)) for s in scores_data) / total_subs) if total_subs > 0 else 0.0
        active_courses = len(set([normalize_course_name(s.get("branch", "")) for s in scores_data])) if scores_data else 0

        m1, m2, m3 = st.columns(3)
        m1.metric("Total Candidates Submitted", f"{total_subs}")
        m2.metric("Average Score", f"{avg_score:.2f}")
        m3.metric("Participating Courses", f"{active_courses}")

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        if not scores_data:
            st.info("ℹ️ No examination records submitted yet. Click 'Refresh Submissions' above to fetch any incoming responses.")
        else:
            results_list = []
            for item in scores_data:
                results_list.append({
                    "Roll No": item["roll_no"],
                    "Candidate Name": item["name"],
                    "Course": normalize_course_name(item["branch"]),
                    "Final Score": float(item.get("score", 0)),
                    "Correct": item.get("correct", 0),
                    "Incorrect": item.get("wrong", 0),
                    "Status": item.get("status", "Completed")
                })
            df = pd.DataFrame(results_list)
            branches = sorted(df["Course"].unique().tolist())
            selected_branch = st.selectbox("Filter Submissions by Course", ["All Courses"] + branches)

            if selected_branch != "All Courses":
                df = df[df["Course"] == selected_branch]
            st.dataframe(df, use_container_width=True)

            st.divider()
            st.markdown("#### 🗑️ Revoke Candidate Submission (Allow Retake)")
            student_options = [f"{item['roll_no']} - {item['name']} ({normalize_course_name(item['branch'])})" for item in scores_data]

            with st.form("delete_student_form"):
                student_to_delete = st.selectbox("Select Candidate Record to Purge", student_options)
                if st.form_submit_button("Revoke & Allow Retake"):
                    if student_to_delete:
                        roll_to_delete = student_to_delete.split(" - ")[0]
                        try:
                            delete_student_score(roll_to_delete)
                            st.toast(f"✅ Record for {roll_to_delete} removed.", icon="🗑️")
                            time.sleep(0.6)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Database error: {e}")

    # 2. CREATE QUESTION
    with tab2:
        st.subheader("Create Assessment Item")
        with st.form("add_question_form"):
            target_branch = st.text_input("Target Course & Semester", placeholder="e.g. BTech 5th Sem")
            q_text = st.text_area("Question Stem / Description", placeholder="Enter question text or code snippet...")

            col_a, col_b = st.columns(2)
            with col_a:
                q_type = st.selectbox("Question Classification", ["MCQ", "MSQ", "Numerical"])
            with col_b:
                marks = st.selectbox("Assigned Marks", [1, 2],
                                     help="MCQ deducts 25% penalty for wrong answers. MSQ & Numerical carry zero negative marking.")

            if q_type == "Numerical":
                q_unit = st.text_input("Unit of Measure (Optional - e.g., ns, kg, m/s, %)")
            else:
                q_unit = ""

            options_input = st.text_input("Answer Choices (Comma-separated for MCQ/MSQ; leave blank for Numerical)",
                                          placeholder="Option A, Option B, Option C, Option D")
            correct_input = st.text_input(
                "Key / Correct Answer (For MSQ, comma-separated; for Numerical, enter exact numeric value)",
                placeholder="Correct answer here")

            st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
            submitted = st.form_submit_button("💾 Save Question to Bank", type="primary")

            if submitted:
                if not q_text or not correct_input or not target_branch:
                    st.error("Course & Semester, question text, and correct answer are mandatory.")
                else:
                    normalized_target_branch = normalize_course_name(target_branch, existing_branches)
                    options = [opt.strip() for opt in options_input.split(",")] if options_input else []
                    is_valid = True

                    if q_type == "MSQ":
                        correct_ans = [ans.strip() for ans in correct_input.split(",")]
                    elif q_type == "Numerical":
                        try:
                            correct_ans = float(correct_input)
                        except ValueError:
                            st.error("❌ For Numerical questions, specify ONLY a valid numeric value.")
                            is_valid = False
                    else:
                        correct_ans = correct_input.strip()

                    if is_valid:
                        new_question = {
                            "branch": normalized_target_branch,
                            "text": q_text,
                            "type": q_type,
                            "marks": marks,
                            "options": options,
                            "correct": correct_ans,
                            "unit": q_unit.strip()
                        }
                        try:
                            add_question(new_question)
                            st.toast(f"✅ Question saved for {normalized_target_branch}!", icon="🎉")
                            time.sleep(0.6)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Database error: {e}")

    # 3. VIEW/EDIT QUESTIONS
    with tab3:
        st.subheader("Manage Existing Questions")
        if not existing_branches:
            st.info("ℹ️ No questions currently populated in the database.")
        else:
            branch_to_edit = st.selectbox("Filter Question Bank by Branch", existing_branches)
            branch_questions = [q for q in questions if normalize_course_name(q.get("branch", "")).lower() == branch_to_edit.lower()]

            if not branch_questions:
                st.info("No items found for this selected course.")
            else:
                for idx, q in enumerate(branch_questions):
                    with st.expander(f"Item #{idx + 1}: {q['text'][:65]}... ({q['type']} | {q['marks']} Marks)"):
                        with st.form(key=f"edit_form_{q['id']}"):
                            edit_q_text = st.text_area("Question Text", value=q['text'])

                            col_a, col_b, col_c = st.columns(3)
                            with col_a:
                                edit_q_type = st.selectbox("Type", ["MCQ", "MSQ", "Numerical"],
                                                           index=["MCQ", "MSQ", "Numerical"].index(q['type']))
                            with col_b:
                                edit_marks = st.selectbox("Marks", [1, 2], index=[1, 2].index(q['marks']))
                            with col_c:
                                edit_unit = st.text_input("Unit", value=q.get('unit', ''))

                            edit_options = st.text_input("Options (Comma-separated)",
                                                         value=",".join(q.get('options') or []))

                            if q['type'] == 'MSQ' and isinstance(q['correct'], list):
                                c_val = ",".join(q['correct'])
                            else:
                                c_val = str(q['correct'])

                            edit_correct = st.text_input("Correct Answer", value=c_val)

                            c1, c2 = st.columns(2)
                            with c1:
                                save_edit = st.form_submit_button("💾 Update Changes", type="primary")
                            with c2:
                                delete_q = st.form_submit_button("🗑️ Delete Question")

                            if save_edit:
                                is_valid = True
                                if edit_q_type == "MSQ":
                                    parsed_correct = [ans.strip() for ans in edit_correct.split(",")]
                                elif edit_q_type == "Numerical":
                                    try:
                                        parsed_correct = float(edit_correct)
                                    except ValueError:
                                        st.error("❌ For Numerical questions, specify ONLY a valid numeric value.")
                                        is_valid = False
                                else:
                                    parsed_correct = edit_correct.strip()

                                if is_valid:
                                    updated_payload = {
                                        "text": edit_q_text,
                                        "type": edit_q_type,
                                        "marks": edit_marks,
                                        "options": [opt.strip() for opt in edit_options.split(",")] if edit_options else [],
                                        "correct": parsed_correct,
                                        "unit": edit_unit.strip()
                                    }
                                    try:
                                        update_question(q['id'], updated_payload)
                                        st.toast("✅ Question updated successfully!", icon="💾")
                                        time.sleep(0.6)
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Database error: {e}")

                            if delete_q:
                                try:
                                    delete_question(q['id'])
                                    st.toast("🗑️ Question deleted from bank.", icon="🗑️")
                                    time.sleep(0.6)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Database error: {e}")

    # 4. QUIZ SETTINGS & PASSKEY
    with tab4:
        st.subheader("Quiz Passkeys & Time Window Configurations")
        if not existing_branches:
            st.info("Please create questions for a branch before configuring policies.")
        else:
            branch_for_timer = st.selectbox("Target Course / Branch", existing_branches)
            current_settings = get_branch_settings(branch_for_timer)

            with st.form("settings_passkey_form"):
                time_limit = st.number_input(
                    "Examination Time Limit (in minutes; enter 0 for unlimited)",
                    min_value=0,
                    value=current_settings.get("time_limit", 30)
                )
                passkey_input = st.text_input(
                    "🔑 Examination Access Passkey (Students must enter this to start)",
                    value=current_settings.get("passkey", ""),
                    placeholder="e.g. BTECH-SPRING-2026"
                )

                st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
                if st.form_submit_button("🔐 Apply Security Settings", type="primary"):
                    try:
                        save_branch_settings(branch_for_timer, time_limit, passkey_input)
                        st.toast(f"✅ Security settings for '{branch_for_timer}' saved!", icon="🔐")
                        time.sleep(0.6)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Database error: {e}")

            st.divider()
            st.markdown("#### 📋 Current Active Course Configurations")
            all_cfg = get_all_settings()
            if all_cfg:
                formatted_cfg = []
                for c in all_cfg:
                    formatted_cfg.append({
                        "Course / Branch": normalize_course_name(c.get("branch", "")),
                        "Time Limit (Mins)": c.get("time_limit", 30),
                        "Active Passkey": c.get("passkey", "")
                    })
                df_cfg = pd.DataFrame(formatted_cfg)
                st.dataframe(df_cfg, use_container_width=True)

    # 5. DANGER ZONE
    with tab5:
        st.subheader("Administrative Danger Zone")
        if existing_branches:
            branch_to_delete = st.selectbox("Select Course Assessment Suite to Delete", existing_branches)
            confirm_branch = st.checkbox(
                f"I understand this deletes all questions, scores, and settings for {branch_to_delete}")
            if st.button("🗑️ Permanently Delete Course Assessment"):
                if confirm_branch:
                    try:
                        delete_branch_data(branch_to_delete)
                        st.toast(f"✅ Deleted all records for {branch_to_delete}.", icon="🗑️")
                        time.sleep(0.6)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Database error: {e}")
                else:
                    st.error("Please confirm the deletion checkbox first.")

        st.divider()
        st.markdown("#### 🚨 Total System Purge")
        confirm_all = st.checkbox(
            "Confirm complete system wipe (Deletes all branches, question banks, and submissions)")
        if st.button("🚨 Wipe Entire Portal Database"):
            if confirm_all:
                try:
                    wipe_all_data()
                    st.toast("✅ System database completely cleared.", icon="🚨")
                    time.sleep(0.6)
                    st.rerun()
                except Exception as e:
                    st.error(f"Database error: {e}")
            else:
                st.error("Please confirm the wipe checkbox first.")


# --- CANDIDATE DASHBOARD ---
def candidate_dashboard():
    student_branch = normalize_course_name(st.session_state.student_info.get('Branch', ''))
    roll_no = st.session_state.user_id

    col1, col2 = st.columns([3.5, 1])
    with col1:
        st.markdown(f"<h2 style='margin:0;'>📝 Examination: {html.escape(student_branch)}</h2>", unsafe_allow_html=True)
        st.markdown(
            f"<div style='font-size: 0.95rem; color: #475569; margin-top: 4px;'>Candidate: <b>{html.escape(st.session_state.student_info.get('Name', ''))}</b> &nbsp;|&nbsp; Roll ID: <code>{html.escape(roll_no)}</code> &nbsp;|&nbsp; Section: <b>{html.escape(st.session_state.student_info.get('Section', ''))}</b></div>",
            unsafe_allow_html=True)
    with col2:
        st.button("🚪 Exit", on_click=logout, use_container_width=True)

    st.write("---")

    my_questions = get_questions_by_branch(student_branch)
    student_record = get_student_score(roll_no)

    # -------------------------------------------------------------
    # IF QUIZ ALREADY SUBMITTED: SHOW RESULT SCREEN & FULL REVIEW
    # -------------------------------------------------------------
    if student_record is not None:
        is_violation = ("Tab Switch" in str(student_record.get("status", "")))

        if is_violation:
            st.markdown("""
                <div class="warning-card">
                    <div style="font-size: 2rem; margin-bottom: 4px;">🚨</div>
                    <h3 style="color: #991b1b; margin: 0 0 6px 0;">Quiz Submitted Under Proctoring Violation</h3>
                    <p style="margin: 0; font-size: 0.95rem; line-height: 1.5;">
                        <b>Cheating Prevention Limit Exceeded:</b> You navigated away from or minimized the examination window 2 times. 
                        Your examination was locked and submitted to the instructor database.
                    </p>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 16px; padding: 20px; text-align: center; margin-bottom: 24px;">
                    <div style="font-size: 2.2rem;">🎉</div>
                    <h2 style="color: #166534; margin: 4px 0 0 0;">Assessment Completed Successfully</h2>
                    <p style="color: #15803d; font-size: 0.95rem; margin: 4px 0 0 0;">Your responses have been recorded and graded automatically.</p>
                </div>
            """, unsafe_allow_html=True)

        # Performance Metrics
        total_possible_marks = sum(q.get('marks', 1) for q in my_questions)
        total_items = len(my_questions)
        percentage = (float(student_record['score']) / total_possible_marks * 100) if total_possible_marks > 0 else 0.0

        st.markdown("### 📊 Performance Metrics")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Final Score", f"{student_record['score']} / {total_possible_marks}", delta=f"{percentage:.1f}%")
        m2.metric("Correct Items", f"{student_record.get('correct', 0)} / {total_items}")
        m3.metric("Incorrect Items", f"{student_record.get('wrong', 0)}")
        m4.metric("Penalty Deducted", f"-{student_record.get('deducted', 0.0)}")

        st.divider()

        # Detailed Question & Answer Review Section
        st.markdown("### 📋 Question Paper & Answer Sheet Review")
        st.caption("Review all questions, your selected answers, and the official answer keys below.")

        student_responses = parse_saved_responses(student_record.get("responses"))

        filter_choice = st.radio(
            "Filter Questions:",
            ["All Items", "Correct Only (✔)", "Incorrect Only (❌)", "Unattempted Only (⚪)"],
            horizontal=True
        )

        for i, q in enumerate(my_questions):
            user_ans = student_responses.get(str(i))
            if user_ans is None and q.get("id"):
                user_ans = student_responses.get(str(q.get("id")))

            q_type = q.get("type", "MCQ")
            marks = q.get("marks", 1)
            correct_key = q.get("correct")

            is_unattempted = (user_ans is None or user_ans == "" or user_ans == [])
            is_correct = False

            if not is_unattempted:
                if q_type == "MCQ":
                    is_correct = (str(user_ans).strip() == str(correct_key).strip())
                elif q_type == "MSQ":
                    correct_set = set(str(c).strip() for c in (correct_key if isinstance(correct_key, list) else [correct_key]))
                    ans_set = set(str(u).strip() for u in (user_ans if isinstance(user_ans, list) else [user_ans]))
                    is_correct = (ans_set == correct_set)
                elif q_type == "Numerical":
                    try:
                        is_correct = (float(user_ans) == float(correct_key))
                    except (ValueError, TypeError):
                        is_correct = False

            if filter_choice == "Correct Only (✔)" and not is_correct:
                continue
            if filter_choice == "Incorrect Only (❌)" and (is_correct or is_unattempted):
                continue
            if filter_choice == "Unattempted Only (⚪)" and not is_unattempted:
                continue

            if is_unattempted:
                box_class = "review-box review-box-skipped"
                status_badge = "<span class='badge-unattempted'>⚪ Skipped / Unattempted (0 Marks)</span>"
            elif is_correct:
                box_class = "review-box review-box-correct"
                status_badge = f"<span class='badge-correct'>✔ Correct (+{marks} Marks)</span>"
            else:
                box_class = "review-box review-box-wrong"
                if q_type == "MCQ":
                    penalty_text = f"-{marks * 0.25} Marks Penalty"
                else:
                    penalty_text = "0 Marks (No Penalty)"
                status_badge = f"<span class='badge-wrong'>❌ Incorrect ({penalty_text})</span>"

            safe_q_text = html.escape(str(q.get("text", "")))

            st.markdown(f"""
            <div class="{box_class}">
                <div class="question-text-content">
                    <b>Q{i + 1}.</b> {safe_q_text} 
                    <span class='badge-mark'>{marks} Marks</span>
                    {status_badge}
                </div>
            """, unsafe_allow_html=True)

            if q_type in ["MCQ", "MSQ"]:
                options = q.get("options") or []
                for opt in options:
                    opt_str = str(opt).strip()
                    is_this_correct_key = False
                    is_this_user_pick = False

                    if q_type == "MCQ":
                        is_this_correct_key = (opt_str == str(correct_key).strip())
                        is_this_user_pick = (not is_unattempted and opt_str == str(user_ans).strip())
                    else:
                        correct_list = [str(c).strip() for c in (correct_key if isinstance(correct_key, list) else [correct_key])]
                        user_list = [str(u).strip() for u in (user_ans if isinstance(user_ans, list) else [user_ans])] if not is_unattempted else []
                        is_this_correct_key = (opt_str in correct_list)
                        is_this_user_pick = (opt_str in user_list)

                    if is_this_correct_key and is_this_user_pick:
                        row_class = "option-item option-correct-key"
                        status_tag = "<span style='font-size:0.8rem; font-weight:700; color:#166534;'>✔ Your Choice (Correct Key)</span>"
                    elif is_this_correct_key and not is_this_user_pick:
                        row_class = "option-item option-correct-key"
                        status_tag = "<span style='font-size:0.8rem; font-weight:700; color:#166534;'>✔ Official Correct Key</span>"
                    elif not is_this_correct_key and is_this_user_pick:
                        row_class = "option-item option-user-wrong"
                        status_tag = "<span style='font-size:0.8rem; font-weight:700; color:#991b1b;'>❌ Your Choice (Incorrect)</span>"
                    else:
                        row_class = "option-item option-default"
                        status_tag = ""

                    st.markdown(f"""
                        <div class="{row_class}">
                            <span>{html.escape(opt_str)}</span>
                            <span>{status_tag}</span>
                        </div>
                    """, unsafe_allow_html=True)

            elif q_type == "Numerical":
                unit_str = f" {html.escape(q.get('unit', ''))}" if q.get("unit") else ""
                user_display = html.escape(str(user_ans)) if not is_unattempted else "<span style='color:#64748b;'>Not Attempted</span>"
                key_display = html.escape(str(correct_key))

                st.markdown(f"""
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:12px 16px; margin-top:8px;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                        <span style="color:#475569; font-weight:600;">Your Submitted Answer:</span>
                        <b>{user_display}{unit_str}</b>
                    </div>
                    <div style="display:flex; justify-content:space-between; border-top:1px dashed #cbd5e1; padding-top:6px;">
                        <span style="color:#166534; font-weight:600;">Official Correct Key:</span>
                        <b style="color:#166534;">{key_display}{unit_str}</b>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        st.divider()
        st.markdown("### 🏆 Branch Standing & Leaderboard")
        branch_scores = get_branch_scores(student_branch)
        if branch_scores:
            df_leaderboard = pd.DataFrame(
                [{"Candidate Name": d["name"], "Score": float(d["score"])} for d in branch_scores])
            df_leaderboard.index = df_leaderboard.index + 1
            st.dataframe(df_leaderboard, use_container_width=True)
        return

    # -------------------------------------------------------------
    # TAKING THE QUIZ & TIMER RECOVERY
    # -------------------------------------------------------------
    branch_config = get_branch_settings(student_branch)
    time_limit = branch_config.get("time_limit", 30)
    time_expired = False

    # Ensure start_time is restored from session_state, query_params, or initialized
    if not st.session_state.start_time:
        if st.query_params.get("start_time"):
            try:
                st.session_state.start_time = float(st.query_params.get("start_time"))
            except Exception:
                st.session_state.start_time = time.time()
        else:
            st.session_state.start_time = time.time()
        st.query_params["start_time"] = str(int(st.session_state.start_time))

    if time_limit > 0:
        elapsed_seconds = int(time.time() - st.session_state.start_time)
        remaining_seconds = max(0, int((time_limit * 60) - elapsed_seconds))

        if remaining_seconds <= 0:
            st.error("⏱️ Allocated examination time has expired. Question inputs are locked. Please submit your exam.")
            time_expired = True
    else:
        remaining_seconds = 999999

    # Check persisted violation strikes from query parameters
    current_strikes = int(st.query_params.get("strikes", "0"))
    is_locked_due_to_violation = (current_strikes >= 2)

    if is_locked_due_to_violation:
        st.markdown("""
        <div class="warning-card">
            <div style="font-size: 1.8rem; margin-bottom: 4px;">🚨</div>
            <h3 style="color: #991b1b; margin: 0 0 6px 0;">Examination Locked: Tab Switch Violations Exceeded (2/2)</h3>
            <p style="margin: 0; font-size: 0.95rem; line-height: 1.5;">
                You have switched tabs twice during this assessment. Further question edits are strictly locked.
                <br/><b>You must now finalize and submit your examination using the submit button below.</b>
            </p>
        </div>
        """, unsafe_allow_html=True)

    inputs_disabled = (time_expired or is_locked_due_to_violation)

    js_roll_no = json.dumps(roll_no)
    js_student_name = json.dumps(st.session_state.student_info.get("Name", ""))
    js_student_branch = json.dumps(student_branch)

    # PERSISTENT REAL-TIME PROCTORING COMPONENT WITH CLIENT-SIDE LOCKING & FORCED SUBMIT
    proctor_component_code = f"""
    <div style="
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
        border-radius: 14px;
        padding: 14px 20px;
        text-align: center;
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #ffffff;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 12px;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
            <div>
                <span style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.08em; color: #a5b4fc; font-weight: 600;">Time Remaining</span><br/>
                <span id="quiz-countdown" style="font-family: 'Outfit', sans-serif; font-weight: 800; font-size: 1.7rem; color: #38bdf8; letter-spacing: -0.02em;">--:--</span>
            </div>
            <div id="proctor-badge" style="
                background: #eef2ff;
                color: #4338ca;
                padding: 6px 14px;
                border-radius: 9999px;
                font-size: 0.78rem;
                font-weight: 700;
                border: 1px solid #c7d2fe;
                transition: all 0.3s ease;
            ">
                🟢 Proctoring Shield Active • 0 Violations
            </div>
        </div>
    </div>

    <script>
        const rollNo = {js_roll_no};
        const strikeKey = "quiz_strikes_" + rollNo;

        // 1. COUNTDOWN TIMER
        let remaining = {remaining_seconds};
        const display = document.getElementById('quiz-countdown');

        function formatTime(secs) {{
            const m = Math.floor(secs / 60);
            const s = secs % 60;
            return (m < 10 ? '0' : '') + m + 'm ' + (s < 10 ? '0' : '') + s + 's';
        }}

        function tick() {{
            if (remaining <= 0) {{
                display.innerText = "00m 00s (Time Over)";
                display.style.color = "#f87171";
                clearInterval(timerInterval);
                return;
            }}
            if (remaining <= 120) {{
                display.style.color = "#f87171";
            }}
            display.innerText = formatTime(remaining);
            remaining--;
        }}
        tick();
        const timerInterval = setInterval(tick, 1000);

        // 2. PERSISTENT PROCTORING ENGINE (Survives refreshes via localStorage)
        let strikes = parseInt(localStorage.getItem(strikeKey) || "0", 10);
        let isAway = false;
        let leaveTimestamp = 0;

        function syncStrikesToParentUrl(s) {{
            try {{
                if (window.parent && window.parent.location) {{
                    const u = new URL(window.parent.location.href);
                    if (u.searchParams.get("strikes") !== String(s)) {{
                        u.searchParams.set("strikes", String(s));
                        window.parent.history.replaceState(null, "", u.toString());
                    }}
                }}
            }} catch(e) {{}}
        }}

        function updateProctorBadge() {{
            const badge = document.getElementById("proctor-badge");
            if (!badge) return;
            if (strikes === 0) {{
                badge.innerHTML = "🟢 Proctoring Shield Active • 0 Violations";
                badge.style.background = "#eef2ff";
                badge.style.color = "#4338ca";
                badge.style.borderColor = "#c7d2fe";
            }} else if (strikes === 1) {{
                badge.innerHTML = "⚠️ Strike 1/2 Recorded • Next Switch = Lock Exam";
                badge.style.background = "#fee2e2";
                badge.style.color = "#991b1b";
                badge.style.borderColor = "#f87171";
            }} else {{
                badge.innerHTML = "🚨 Strike 2/2 • Exam Locked (Submission Required)";
                badge.style.background = "#991b1b";
                badge.style.color = "#ffffff";
                badge.style.borderColor = "#7f1d1d";
            }}
        }}
        updateProctorBadge();
        syncStrikesToParentUrl(strikes);

        function playAlertTone() {{
            try {{
                const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.type = "sawtooth";
                osc.frequency.setValueAtTime(440, audioCtx.currentTime);
                osc.frequency.setValueAtTime(880, audioCtx.currentTime + 0.15);
                gain.gain.setValueAtTime(0.25, audioCtx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.45);
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start();
                osc.stop(audioCtx.currentTime + 0.45);
            }} catch(e) {{}}
        }}

        function showWarningModal(awayDuration) {{
            playAlertTone();
            const targetDoc = (window.parent && window.parent.document) ? window.parent.document : document;
            
            const existing = targetDoc.getElementById("proctor-warning-modal-overlay");
            if (existing) existing.remove();

            const overlay = targetDoc.createElement("div");
            overlay.id = "proctor-warning-modal-overlay";
            overlay.style.cssText = "position:fixed; top:0; left:0; width:100vw; height:100vh; background:rgba(15,23,42,0.85); backdrop-filter:blur(8px); z-index:99999999; display:flex; align-items:center; justify-content:center; font-family:'Plus Jakarta Sans', sans-serif;";
            
            overlay.innerHTML = '<div style="background:#ffffff; border-radius:20px; max-width:520px; width:90%; padding:32px 28px; text-align:center; box-shadow:0 25px 50px -12px rgba(220,38,38,0.35); border:2px solid #ef4444;">' +
                '<div style="font-size:3.2rem; line-height:1; margin-bottom:10px;">⚠️</div>' +
                '<h2 style="color:#991b1b; font-size:1.55rem; font-weight:800; margin:0 0 10px 0;">PROCTORING VIOLATION DETECTED</h2>' +
                '<div style="background:#fef2f2; border:1px solid #fecaca; border-radius:12px; padding:10px 16px; color:#b91c1c; font-weight:700; font-size:0.92rem; margin-bottom:14px;">' +
                    'Strike 1 of 2 Recorded • Left Window for ' + awayDuration + 's' +
                '</div>' +
                '<p style="color:#475569; font-size:0.95rem; line-height:1.6; margin-bottom:22px;">' +
                    'You switched tabs or navigated away from the examination window. Navigating to external applications is strictly prohibited.' +
                    '<br/><br/><b style="color:#dc2626;">This is your final warning. If you switch tabs or leave one more time, your exam will be permanently locked and you will be forced to submit immediately.</b>' +
                '</p>' +
                '<button id="ack-warning-btn" style="background:linear-gradient(135deg, #dc2626 0%, #b91c1c 100%); color:#ffffff; border:none; padding:13px 26px; font-size:1rem; font-weight:700; border-radius:12px; cursor:pointer; width:100%; box-shadow:0 4px 14px rgba(220,38,38,0.3);">' +
                    'I Understand & Acknowledge (Return to Quiz)' +
                '</button>' +
            '</div>';

            targetDoc.body.appendChild(overlay);

            const ackBtn = targetDoc.getElementById("ack-warning-btn");
            if (ackBtn) {{
                ackBtn.onclick = function() {{
                    overlay.remove();
                }};
            }}
        }}

        // LOCK QUIZ AND REQUIRE CANDIDATE TO SUBMIT (NO AUTO-SUBMIT)
        function lockAndRequireSubmission() {{
            playAlertTone();
            const targetDoc = (window.parent && window.parent.document) ? window.parent.document : document;

            // Disable all input fields on parent page
            const questionInputs = targetDoc.querySelectorAll('.question-box input, .question-box button');
            questionInputs.forEach(el => {{
                el.disabled = true;
            }});

            const existingWarn = targetDoc.getElementById("proctor-warning-modal-overlay");
            if (existingWarn) existingWarn.remove();

            let lockOverlay = targetDoc.getElementById("proctor-force-lock-overlay");
            if (!lockOverlay) {{
                lockOverlay = targetDoc.createElement("div");
                lockOverlay.id = "proctor-force-lock-overlay";
                lockOverlay.style.cssText = "position:fixed; top:0; left:0; width:100vw; height:100vh; background:rgba(15,23,42,0.92); backdrop-filter:blur(8px); z-index:99999999; display:flex; align-items:center; justify-content:center; font-family:'Plus Jakarta Sans', sans-serif;";
                
                lockOverlay.innerHTML = '<div style="background:#ffffff; border-radius:20px; max-width:520px; width:90%; padding:36px 28px; text-align:center; box-shadow:0 25px 50px -12px rgba(220,38,38,0.4); border:2px solid #ef4444;">' +
                    '<div style="font-size:3.5rem; line-height:1; margin-bottom:12px;">🚨</div>' +
                    '<h2 style="color:#991b1b; font-size:1.6rem; font-weight:800; margin:0 0 10px 0;">EXAMINATION LOCKED</h2>' +
                    '<div style="background:#fee2e2; border:1px solid #fca5a5; border-radius:12px; padding:10px 16px; color:#991b1b; font-weight:700; font-size:0.92rem; margin-bottom:16px;">' +
                        'Proctoring Limit Exceeded (Strike 2 of 2)' +
                    '</div>' +
                    '<p style="color:#475569; font-size:0.95rem; line-height:1.6; margin-bottom:24px;">' +
                        'You navigated away from the exam window again after receiving your final warning. Your test is locked and questions can no longer be modified.' +
                        '<br/><br/><b style="color:#b91c1c;">You must now submit your examination to record your score.</b>' +
                    '</p>' +
                    '<button id="candidate-submit-now-btn" style="background:linear-gradient(135deg, #dc2626 0%, #b91c1c 100%); color:#ffffff; border:none; padding:14px 28px; font-size:1.05rem; font-weight:700; border-radius:12px; cursor:pointer; width:100%; box-shadow:0 4px 14px rgba(220,38,38,0.35);">' +
                        '📤 Finalize & Submit Examination Now' +
                    '</button>' +
                '</div>';
                targetDoc.body.appendChild(lockOverlay);

                const subNowBtn = targetDoc.getElementById("candidate-submit-now-btn");
                if (subNowBtn) {{
                    subNowBtn.onclick = function() {{
                        subNowBtn.disabled = true;
                        subNowBtn.innerText = "Processing Submission...";
                        // Trigger the form submit button in Streamlit
                        const allBtns = targetDoc.querySelectorAll('button[kind="primary"]');
                        for (let b of allBtns) {{
                            if (b.innerText.includes("Submit") || b.innerText.includes("Finalize")) {{
                                b.disabled = false;
                                b.click();
                                return;
                            }}
                        }}
                    }};
                }}
            }}
        }}

        // If page is loaded or refreshed and candidate is already at 2 strikes, lock immediately
        if (strikes >= 2) {{
            lockAndRequireSubmission();
        }}

        function handleTabDeparture() {{
            if (!isAway) {{
                isAway = true;
                leaveTimestamp = Date.now();
                
                if (strikes >= 1) {{
                    strikes = 2;
                    localStorage.setItem(strikeKey, "2");
                    syncStrikesToParentUrl(2);
                    updateProctorBadge();
                    lockAndRequireSubmission();
                }}
            }}
        }}

        function handleTabReturn() {{
            if (isAway) {{
                isAway = false;
                const awaySecs = Math.max(1, Math.round((Date.now() - leaveTimestamp) / 1000));
                
                if (strikes === 0) {{
                    strikes = 1;
                    localStorage.setItem(strikeKey, "1");
                    syncStrikesToParentUrl(1);
                    updateProctorBadge();
                    showWarningModal(awaySecs);
                }} else if (strikes >= 2) {{
                    lockAndRequireSubmission();
                }}
            }}
        }}

        document.addEventListener("visibilitychange", function() {{
            if (document.hidden) {{
                handleTabDeparture();
            }} else {{
                handleTabReturn();
            }}
        }});

        try {{
            if (window.parent && window.parent.document) {{
                window.parent.document.addEventListener("visibilitychange", function() {{
                    if (window.parent.document.hidden) {{
                        handleTabDeparture();
                    }} else {{
                        handleTabReturn();
                    }}
                }});
                
                window.parent.addEventListener("blur", function() {{
                    setTimeout(() => {{
                        if (window.parent && window.parent.document && window.parent.document.hidden) {{
                            handleTabDeparture();
                        }}
                    }}, 300);
                }});
            }}
        }} catch(e) {{}}
    </script>
    """
    components.html(proctor_component_code, height=100)

    # Standard Exam Form Submission
    def finalize_normal_exam(user_ans_dict, is_late=False):
        score = 0.0
        correct_count = 0
        wrong_count = 0
        total_deducted = 0.0
        saved_responses = {}

        for i, q in enumerate(my_questions):
            ans = user_ans_dict.get(i)
            marks = q["marks"]
            saved_responses[str(i)] = ans

            if ans is None or ans == [] or ans == "":
                continue

            is_correct = False
            if q["type"] == "MCQ":
                is_correct = (str(ans).strip() == str(q["correct"]).strip())
            elif q["type"] == "MSQ":
                correct_set = set(str(c).strip() for c in (q["correct"] if isinstance(q["correct"], list) else [q["correct"]]))
                ans_set = set(str(a).strip() for a in (ans if isinstance(ans, list) else [ans]))
                is_correct = (ans_set == correct_set)
            elif q["type"] == "Numerical":
                try:
                    is_correct = (float(ans) == float(q["correct"]))
                except (ValueError, TypeError):
                    is_correct = False

            if is_correct:
                score += marks
                correct_count += 1
            else:
                wrong_count += 1
                if q["type"] == "MCQ":
                    penalty = (marks * 0.25)
                    score -= penalty
                    total_deducted += penalty

        # Determine appropriate status
        final_strikes = int(st.query_params.get("strikes", "0"))
        if final_strikes >= 2:
            status_desc = "Submitted (Tab Switch Violation)"
        elif is_late:
            status_desc = "Rejected (Late Submission)"
        else:
            status_desc = "Completed"

        final_record = {
            "roll_no": roll_no,
            "name": st.session_state.student_info.get("Name", ""),
            "section": st.session_state.student_info.get("Section", ""),
            "branch": student_branch,
            "score": score,
            "correct": correct_count,
            "wrong": wrong_count,
            "deducted": total_deducted,
            "responses": saved_responses,
            "status": status_desc
        }
        try:
            save_student_score(final_record)
            time.sleep(0.4)
            st.rerun()
        except Exception as e:
            st.error(f"Failed to record examination score: {e}")

    # EXAM FORM
    with st.form("quiz_form"):
        user_answers = {}
        for i, q in enumerate(my_questions):
            safe_text = html.escape(q['text'])
            st.markdown("<div class='question-box'>", unsafe_allow_html=True)

            if q["type"] == "MCQ":
                neg_badge = f"<span class='badge-neg'>-{q['marks'] * 0.25} Negative Mark</span>"
            else:
                neg_badge = "<span class='badge-mark'>No Negative Penalty</span>"

            st.markdown(
                f"<div class='question-text-content'>Q{i + 1}. {safe_text} <span class='badge-mark'>{q['marks']} Marks</span> {neg_badge}</div>",
                unsafe_allow_html=True)

            if q["type"] == "MCQ":
                user_answers[i] = st.radio(f"Options for Q{i + 1}", q.get("options") or [], index=None, key=f"q_{i}",
                                           label_visibility="collapsed", disabled=inputs_disabled)
            elif q["type"] == "MSQ":
                user_answers[i] = st.multiselect(f"Options for Q{i + 1}", q.get("options") or [], key=f"q_{i}",
                                                 label_visibility="collapsed", disabled=inputs_disabled)
            elif q["type"] == "Numerical":
                col_input, col_unit = st.columns([2, 5])
                with col_input:
                    user_answers[i] = st.text_input(f"Answer for Q{i + 1}", key=f"q_{i}", label_visibility="collapsed",
                                                    disabled=inputs_disabled, placeholder="Numeric value")
                with col_unit:
                    if q.get("unit"):
                        st.markdown(
                            f"<div style='padding-top:6px; font-weight: 600; color: #475569;'>{html.escape(q['unit'])}</div>",
                            unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        # Notice: Submit button remains active so candidate can always submit even when locked!
        submit_btn = st.form_submit_button("✅ Finalize & Submit Examination", type="primary",
                                           use_container_width=True)

        if submit_btn:
            if time_limit > 0:
                final_elapsed = time.time() - (st.session_state.start_time or time.time())
                if final_elapsed > (time_limit * 60) + 10:
                    st.error("Submission marked as late due to time elapsed.")
                    finalize_normal_exam(user_answers, is_late=True)
                    return

            finalize_normal_exam(user_answers, is_late=False)


# --- ROUTER ---
if not st.session_state.logged_in:
    login_screen()
else:
    if st.session_state.role == "admin":
        admin_dashboard()
    else:
        candidate_dashboard()
