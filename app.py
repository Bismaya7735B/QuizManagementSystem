import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import time
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

    /* Modern Glassmorphic Question Card */
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
    }

    /* Segmented Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: #f1f5f9;
        padding: 6px;
        border-radius: 14px;
        border: 1px solid #e2e8f0;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 10px;
        padding: 8px 18px;
        color: #64748b;
        font-weight: 600;
        border: none !important;
        transition: all 0.2s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #1e293b;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff !important;
        color: #4338ca !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.08), 0 2px 4px -2px rgba(0, 0, 0, 0.04);
    }

    /* Enterprise Metric Cards */
    [data-testid="stMetric"] {
        background: #ffffff;
        border-radius: 16px;
        padding: 16px 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0;
        transition: transform 0.2s ease;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
    }
    [data-testid="stMetricValue"] {
        font-family: 'Outfit', sans-serif !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #1e1b4b;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        color: #64748b !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Primary Buttons Styling */
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
    .stButton > button[kind="primary"]:active {
        transform: translateY(0px) !important;
    }

    /* Secondary / Logout Buttons */
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }

    /* Input Field Polish */
    .stTextInput > div > div > input, 
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {
        border-radius: 10px !important;
        border: 1px solid #cbd5e1 !important;
        background-color: #ffffff !important;
        font-size: 0.95rem !important;
    }
    .stTextInput > div > div > input:focus, 
    .stTextArea > div > div > textarea:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2) !important;
    }

    /* Expander Styling */
    .streamlit-expanderHeader {
        background-color: #ffffff !important;
        border-radius: 12px !important;
        border: 1px solid #e2e8f0 !important;
        font-weight: 600 !important;
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
        res = supabase.table("scores").select("*").execute()
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


# --- SESSION STATE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = ""
    st.session_state.role = ""
    st.session_state.student_info = {}
if "start_time" not in st.session_state:
    st.session_state.start_time = None


# --- LOGIN SCREEN ---
def login_screen():
    st.markdown("""
    <div class="hero-banner">
        <div style="font-size: 2.8rem; margin-bottom: 8px;">🎓</div>
        <h1 class="hero-title">Pro Quiz Portal</h1>
        <p class="hero-subtitle">Enterprise Online Assessment & Examination System</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["👨‍🎓 Candidate Access", "🔐 Administrator Portal"])
    
    # 1. CANDIDATE ENTRY
    with tab1:
        st.markdown("<p style='font-size: 0.95rem; color: #475569; margin-bottom: 12px;'>Enter your student credentials and authorized passkey to begin your examination.</p>", unsafe_allow_html=True)
        with st.form("student_login_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Full Name", placeholder="e.g. John Doe")
                rollno = st.text_input("Roll Number", placeholder="e.g. 23BCA042")
            with col2:
                section = st.text_input("Section", placeholder="e.g. Section A")
                branch = st.text_input("Course & Semester", placeholder="e.g. BCA 2nd Sem")
                
            student_passkey = st.text_input("🔑 Quiz Passkey (Issued by Instructor)", type="password", placeholder="Enter authorization passkey")
            
            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
            submit_student = st.form_submit_button("🚀 Start Assessment", type="primary", use_container_width=True)
            
            if submit_student:
                if not (name and rollno and section and branch):
                    st.error("⚠️ Please fill in all candidate details.")
                else:
                    branch_questions = get_questions_by_branch(branch)
                    if not branch_questions:
                        st.error(f"❌ No active quiz found for '{branch.strip()}'. Please check the exact course and semester name.")
                    else:
                        branch_config = get_branch_settings(branch)
                        required_passkey = branch_config.get("passkey", "")
                        
                        if required_passkey and student_passkey.strip() != required_passkey:
                            st.error("❌ Invalid Quiz Passkey. Please verify with your instructor.")
                        else:
                            st.session_state.logged_in = True
                            st.session_state.role = "candidate"
                            st.session_state.user_id = rollno.strip().upper()
                            st.session_state.student_info = {
                                "Name": name.strip(),
                                "Roll No": rollno.strip().upper(),
                                "Section": section.strip(),
                                "Branch": branch.strip()
                            }
                            st.session_state.start_time = time.time()
                            st.rerun()
                    
    # 2. ADMIN LOGIN
    with tab2:
        st.markdown("<p style='font-size: 0.95rem; color: #475569; margin-bottom: 12px;'>Authorized instructor and administrator access only.</p>", unsafe_allow_html=True)
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
                    st.rerun()
                else:
                    st.error("❌ Invalid administrative credentials.")


# --- ADMIN DASHBOARD ---
def admin_dashboard():
    col1, col2 = st.columns([3.5, 1])
    with col1:
        st.markdown("<h2 style='margin:0;'>⚙️ Examination Control Center</h2>", unsafe_allow_html=True)
        st.caption("Manage questions, branch security passkeys, durations, and student submissions.")
    with col2:
        st.button("🚪 Log Out", on_click=logout, use_container_width=True)
    
    st.write("---")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "➕ Add Question", 
        "✏️ Question Bank", 
        "🔐 Passkey & Limits", 
        "📊 Score Analytics", 
        "🗑️ Data Management"
    ])
    
    questions = get_all_questions()
    existing_branches = sorted(list(set([q["branch"] for q in questions if q.get("branch")])))

    # 1. CREATE QUESTION
    with tab1:
        st.subheader("Create Assessment Item")
        with st.form("add_question_form"):
            target_branch = st.text_input("Target Course & Semester", placeholder="e.g. BCA 2nd Sem")
            q_text = st.text_area("Question Stem / Description", placeholder="Enter the complete question text here...")
            
            col_a, col_b = st.columns(2)
            with col_a:
                q_type = st.selectbox("Question Classification", ["MCQ", "MSQ", "Numerical"])
            with col_b:
                marks = st.selectbox("Assigned Marks", [1, 2], help="MCQ deducts 25% penalty for wrong answers. MSQ & Numerical carry zero negative marking.")
            
            if q_type == "Numerical":
                q_unit = st.text_input("Unit of Measure (Optional - e.g., ns, kg, m/s, %)")
            else:
                q_unit = ""
                
            options_input = st.text_input("Answer Choices (Comma-separated for MCQ/MSQ; leave blank for Numerical)", placeholder="Option A, Option B, Option C, Option D")
            correct_input = st.text_input("Key / Correct Answer (For MSQ, comma-separated; for Numerical, enter exact numeric value)", placeholder="Correct answer here")
            
            st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
            submitted = st.form_submit_button("💾 Save Question to Bank", type="primary")
            
            if submitted:
                if not q_text or not correct_input or not target_branch:
                    st.error("Branch, question text, and correct answer are mandatory.")
                else:
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
                            "branch": target_branch.strip(),
                            "text": q_text,
                            "type": q_type,
                            "marks": marks,
                            "options": options,
                            "correct": correct_ans,
                            "unit": q_unit.strip()
                        }
                        try:
                            add_question(new_question)
                            st.toast(f"✅ Question saved for {target_branch}!", icon="🎉")
                            time.sleep(0.6)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Database error: {e}")

    # 2. VIEW/EDIT QUESTIONS
    with tab2:
        st.subheader("Manage Existing Questions")
        if not existing_branches:
            st.info("ℹ️ No questions currently populated in the database.")
        else:
            branch_to_edit = st.selectbox("Filter Question Bank by Branch", existing_branches)
            branch_questions = [q for q in questions if q.get("branch", "").lower() == branch_to_edit.lower()]
            
            if not branch_questions:
                st.info("No items found for this selected course.")
            else:
                for idx, q in enumerate(branch_questions):
                    with st.expander(f"Item #{idx + 1}: {q['text'][:65]}... ({q['type']} | {q['marks']} Marks)"):
                        with st.form(key=f"edit_form_{q['id']}"):
                            edit_q_text = st.text_area("Question Text", value=q['text'])
                            
                            col_a, col_b, col_c = st.columns(3)
                            with col_a:
                                edit_q_type = st.selectbox("Type", ["MCQ", "MSQ", "Numerical"], index=["MCQ", "MSQ", "Numerical"].index(q['type']))
                            with col_b:
                                edit_marks = st.selectbox("Marks", [1, 2], index=[1, 2].index(q['marks']))
                            with col_c:
                                edit_unit = st.text_input("Unit", value=q.get('unit', ''))
                            
                            edit_options = st.text_input("Options (Comma-separated)", value=",".join(q.get('options') or []))
                            
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

    # 3. QUIZ SETTINGS & PASSKEY
    with tab3:
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
                    placeholder="e.g. BCA-SPRING-2026"
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
                df_cfg = pd.DataFrame(all_cfg)
                df_cfg.columns = ["Course / Branch", "Time Limit (Mins)", "Active Passkey"]
                st.dataframe(df_cfg, use_container_width=True)

    # 4. VIEW RESULTS & MANAGE
    with tab4:
        st.subheader("Student Performance & Records")
        scores_data = get_all_scores()
        if not scores_data:
            st.info("ℹ️ No examination records submitted yet.")
        else:
            results_list = []
            for item in scores_data:
                results_list.append({
                    "Roll No": item["roll_no"],
                    "Candidate Name": item["name"],
                    "Course": item["branch"],
                    "Final Score": float(item["score"]),
                    "Correct": item.get("correct", 0),
                    "Incorrect": item.get("wrong", 0),
                    "Status": item.get("status", "Completed")
                })
            df = pd.DataFrame(results_list)
            branches = sorted(df["Course"].unique().tolist())
            selected_branch = st.selectbox("Filter Leaderboard by Course", ["All Courses"] + branches)
            
            if selected_branch != "All Courses":
                df = df[df["Course"] == selected_branch]
            st.dataframe(df, use_container_width=True)

            st.divider()
            
            st.markdown("#### 🗑️ Revoke Candidate Submission (Allow Retake)")
            student_options = [f"{item['roll_no']} - {item['name']} ({item['branch']})" for item in scores_data]
            
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

    # 5. MANAGE DATA
    with tab5:
        st.subheader("Administrative Danger Zone")
        if existing_branches:
            branch_to_delete = st.selectbox("Select Course Assessment Suite to Delete", existing_branches)
            confirm_branch = st.checkbox(f"I understand this deletes all questions, scores, and settings for {branch_to_delete}")
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
        confirm_all = st.checkbox("Confirm complete system wipe (Deletes all branches, question banks, and submissions)")
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
    student_branch = st.session_state.student_info['Branch']
    roll_no = st.session_state.user_id
    
    col1, col2 = st.columns([3.5, 1])
    with col1:
        st.markdown(f"<h2 style='margin:0;'>📝 Examination: {student_branch}</h2>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size: 0.95rem; color: #475569; margin-top: 4px;'>Candidate: <b>{st.session_state.student_info['Name']}</b> &nbsp;|&nbsp; Roll ID: <code>{roll_no}</code> &nbsp;|&nbsp; Section: <b>{st.session_state.student_info['Section']}</b></div>", unsafe_allow_html=True)
    with col2:
        st.button("🚪 Exit", on_click=logout, use_container_width=True)
    
    st.write("---")
    
    my_questions = get_questions_by_branch(student_branch)
    student_record = get_student_score(roll_no)
    
    # -------------------------------------------------------------
    # IF QUIZ ALREADY SUBMITTED: SHOW RESULT SCREEN & LEADERBOARD
    # -------------------------------------------------------------
    if student_record is not None:
        st.markdown("""
        <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 16px; padding: 20px; text-align: center; margin-bottom: 24px;">
            <div style="font-size: 2.2rem;">🎉</div>
            <h2 style="color: #166534; margin: 4px 0 0 0;">Assessment Completed Successfully</h2>
            <p style="color: #15803d; font-size: 0.95rem; margin: 4px 0 0 0;">Your responses have been recorded and graded automatically.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 📊 Performance Metrics")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Final Score", f"{student_record['score']}")
        m2.metric("Correct Items", f"{student_record.get('correct', 0)}")
        m3.metric("Incorrect Items", f"{student_record.get('wrong', 0)}")
        m4.metric("Penalty Deducted", f"-{student_record.get('deducted', 0.0)}")
        
        st.divider()
        
        st.markdown("### 📝 Detailed Item Review")
        saved_responses = student_record.get("responses") or {}
        
        for i, q in enumerate(my_questions):
            with st.container():
                st.markdown("<div class='question-box'>", unsafe_allow_html=True)
                st.markdown(f"**Item {i+1}: {q['text']}** <span class='badge-mark'>{q['marks']} Marks</span>", unsafe_allow_html=True)
                
                ans = saved_responses.get(str(i), None)
                
                display_ans = ans
                display_correct = q['correct']
                if q["type"] == "MSQ":
                    display_ans = ", ".join(ans) if ans else "None"
                    display_correct = ", ".join(q['correct']) if isinstance(q['correct'], list) else str(q['correct'])
                elif q["type"] == "Numerical":
                    if ans == "" or ans is None: 
                        display_ans = "None"
                    elif q.get("unit"): 
                        display_ans = f"{ans} {q['unit']}"
                    display_correct = f"{q['correct']} {q.get('unit', '')}".strip()
                
                if ans is None or ans == [] or ans == "":
                    st.warning(f"⚪ **Status:** Skipped | **Key:** {display_correct}")
                else:
                    is_correct = False
                    if q["type"] == "MCQ": 
                        is_correct = (ans == q["correct"])
                    elif q["type"] == "MSQ": 
                        is_correct = set(ans) == set(q["correct"])
                    elif q["type"] == "Numerical":
                        try: 
                            is_correct = (float(ans) == float(q["correct"]))
                        except ValueError: 
                            is_correct = False

                    if is_correct:
                        st.success(f"✅ **Correct!** Your Submission: **{display_ans}**")
                    else:
                        st.error(f"❌ **Incorrect.** Your Submission: **{display_ans}** &nbsp;|&nbsp; Correct Answer: **{display_correct}**")
                
                st.markdown("</div>", unsafe_allow_html=True)

        st.divider()

        st.markdown("### 🏆 Branch Standing & Leaderboard")
        branch_scores = get_branch_scores(student_branch)
        if branch_scores:
            df_leaderboard = pd.DataFrame([{"Candidate Name": d["name"], "Score": float(d["score"])} for d in branch_scores])
            df_leaderboard.index = df_leaderboard.index + 1
            st.dataframe(df_leaderboard, use_container_width=True)
        return

    # -------------------------------------------------------------
    # TAKING THE QUIZ
    # -------------------------------------------------------------
    if not my_questions:
        st.warning(f"⚠️ No examination questions are currently configured for '{student_branch}'. Please contact your supervisor.")
        return

    branch_config = get_branch_settings(student_branch)
    time_limit = branch_config.get("time_limit", 30)
    time_expired = False
    
    if time_limit > 0:
        elapsed_seconds = int(time.time() - st.session_state.start_time)
        remaining_seconds = max(0, int((time_limit * 60) - elapsed_seconds))
        
        if remaining_seconds <= 0:
            st.error("⏱️ Allocated examination time has expired. Question inputs are locked.")
            time_expired = True
        else:
            timer_html = f"""
            <div style="
                background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
                border-radius: 14px;
                padding: 14px 20px;
                text-align: center;
                font-family: 'Plus Jakarta Sans', sans-serif;
                color: #ffffff;
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.1);
                margin-bottom: 18px;
            ">
                <span style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.08em; color: #a5b4fc; font-weight: 600;">Time Remaining</span><br/>
                <span id="quiz-countdown" style="font-family: 'Outfit', sans-serif; font-weight: 800; font-size: 1.8rem; color: #38bdf8; letter-spacing: -0.02em;">--:--</span>
            </div>

            <script>
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
                        display.style.color = "#f87171"; // Red alert when under 2 minutes
                    }}
                    display.innerText = formatTime(remaining);
                    remaining--;
                }}

                tick();
                const timerInterval = setInterval(tick, 1000);
            </script>
            """
            components.html(timer_html, height=90)
    
    with st.form("quiz_form"):
        user_answers = {}
        for i, q in enumerate(my_questions):
            st.markdown("<div class='question-box'>", unsafe_allow_html=True)
            
            if q["type"] == "MCQ":
                neg_badge = f"<span class='badge-neg'>-{q['marks'] * 0.25} Negative Mark</span>"
            else:
                neg_badge = "<span class='badge-mark'>No Negative Penalty</span>"
                
            st.markdown(f"<div style='font-size: 1.05rem; font-weight: 600; margin-bottom: 12px;'>Q{i+1}. {q['text']} <span class='badge-mark'>{q['marks']} Marks</span> {neg_badge}</div>", unsafe_allow_html=True)
            
            if q["type"] == "MCQ":
                user_answers[i] = st.radio(f"Options for Q{i+1}", q.get("options") or [], index=None, key=f"q_{i}", label_visibility="collapsed", disabled=time_expired)
            elif q["type"] == "MSQ":
                user_answers[i] = st.multiselect(f"Options for Q{i+1}", q.get("options") or [], key=f"q_{i}", label_visibility="collapsed", disabled=time_expired)
            elif q["type"] == "Numerical":
                col_input, col_unit = st.columns([2, 5])
                with col_input:
                    user_answers[i] = st.text_input(f"Answer for Q{i+1}", key=f"q_{i}", label_visibility="collapsed", disabled=time_expired, placeholder="Numeric value")
                with col_unit:
                    if q.get("unit"):
                        st.markdown(f"<div style='padding-top:6px; font-weight: 600; color: #475569;'>{q['unit']}</div>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        submit_btn = st.form_submit_button("✅ Finalize & Submit Examination", type="primary", disabled=time_expired, use_container_width=True)
        
        if submit_btn:
            if time_limit > 0:
                final_elapsed = time.time() - st.session_state.start_time
                if final_elapsed > (time_limit * 60) + 10: 
                    st.error("Submission rejected. The examination window elapsed.")
                    late_record = {
                        "roll_no": roll_no,
                        "name": st.session_state.student_info["Name"],
                        "section": st.session_state.student_info["Section"],
                        "branch": student_branch,
                        "score": 0.0,
                        "correct": 0,
                        "wrong": 0,
                        "deducted": 0.0,
                        "responses": {},
                        "status": "Rejected (Late Submission)"
                    }
                    try:
                        save_student_score(late_record)
                    except Exception as e:
                        st.error(f"Failed to record late submission: {e}")
                    st.rerun()
                    return

            score = 0.0
            correct_count = 0
            wrong_count = 0
            total_deducted = 0.0
            saved_responses = {}
            
            for i, q in enumerate(my_questions):
                ans = user_answers[i]
                marks = q["marks"]
                saved_responses[str(i)] = ans
                
                if ans is None or ans == [] or ans == "": 
                    continue
                    
                is_correct = False
                if q["type"] == "MCQ": 
                    is_correct = (ans == q["correct"])
                elif q["type"] == "MSQ": 
                    is_correct = set(ans) == set(q["correct"])
                elif q["type"] == "Numerical":
                    try: 
                        is_correct = (float(ans) == float(q["correct"]))
                    except ValueError: 
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

            final_record = {
                "roll_no": roll_no,
                "name": st.session_state.student_info["Name"],
                "section": st.session_state.student_info["Section"],
                "branch": student_branch,
                "score": score,
                "correct": correct_count,
                "wrong": wrong_count,
                "deducted": total_deducted,
                "responses": saved_responses,
                "status": "Completed"
            }
            try:
                save_student_score(final_record)
                st.toast("✅ Examination successfully submitted!", icon="🎉")
                time.sleep(0.6)
                st.rerun()
            except Exception as e:
                st.error(f"Failed to save score: {e}")

def logout():
    st.session_state.logged_in = False
    st.session_state.user_id = ""
    st.session_state.role = ""
    st.session_state.student_info = {}
    st.session_state.start_time = None

# --- ROUTER ---
if not st.session_state.logged_in:
    login_screen()
else:
    if st.session_state.role == "admin": 
        admin_dashboard()
    else: 
        candidate_dashboard()
