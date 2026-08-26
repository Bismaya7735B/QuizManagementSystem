import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import time
from supabase import create_client, Client

# --- PAGE CONFIGURATION & STYLING ---
st.set_page_config(page_title="Pro Quiz Portal", page_icon="🎓", layout="centered")

st.markdown("""
<style>
    .stApp {
        background-color: #f8f9fa;
    }
    h1, h2, h3 {
        color: #1E3A8A;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff;
        border-radius: 4px 4px 0px 0px;
        padding: 10px 20px;
        box-shadow: 0px -2px 5px rgba(0,0,0,0.05);
    }
    .stTabs [aria-selected="true"] {
        background-color: #1E3A8A;
        color: white !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        color: #1E3A8A;
    }
    .question-box {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        border-left: 5px solid #1E3A8A;
    }
</style>
""", unsafe_allow_html=True)

# --- SUPABASE CREDENTIALS ---
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
    st.markdown("<h1 style='text-align: center;'>🎓 Pro Quiz Portal</h1>", unsafe_allow_html=True)
    st.write("---")
    
    tab1, tab2 = st.tabs(["👨🎓 Student Entry", "👨🏫 Admin Login"])
    
    # 1. STUDENT LOGIN
    with tab1:
        st.subheader("Enter your details to start the quiz")
        with st.form("student_login_form"):
            name = st.text_input("Full Name")
            rollno = st.text_input("Roll Number")
            section = st.text_input("Section")
            branch = st.text_input("Course & Semester (e.g., BCA 2nd Sem)")
            student_passkey = st.text_input("🔑 Quiz Passkey (provided by instructor)", type="password")
            
            submit_student = st.form_submit_button("🚀 Start Quiz", type="primary", use_container_width=True)
            
            if submit_student:
                if not (name and rollno and section and branch):
                    st.error("Please fill in all basic student details.")
                else:
                    # Verify if questions exist for this branch
                    branch_questions = get_questions_by_branch(branch)
                    if not branch_questions:
                        st.error(f"❌ No active quiz found for '{branch.strip()}'. Please verify the course/semester name.")
                    else:
                        # Check passkey verification
                        branch_config = get_branch_settings(branch)
                        required_passkey = branch_config.get("passkey", "")
                        
                        if required_passkey and student_passkey.strip() != required_passkey:
                            st.error("❌ Incorrect Quiz Passkey. Please request the passkey from your instructor.")
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
        st.subheader("Admin Access")
        with st.form("admin_login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit_admin = st.form_submit_button("Login", type="primary", use_container_width=True)
            
            if submit_admin:
                if username == "admin" and password == "admin":
                    st.session_state.logged_in = True
                    st.session_state.user_id = "admin"
                    st.session_state.role = "admin"
                    st.rerun()
                else:
                    st.error("Invalid credentials.")


# --- ADMIN DASHBOARD ---
def admin_dashboard():
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title("⚙️ Admin Dashboard")
    with col2:
        st.button("🚪 Logout", on_click=logout, use_container_width=True)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["➕ Create Question", "✏️ View/Edit", "⏱️ Settings & Passkey", "📊 Results", "🗑️ Manage Data"])
    
    questions = get_all_questions()
    existing_branches = sorted(list(set([q["branch"] for q in questions if q.get("branch")])))

    # 1. CREATE QUESTION
    with tab1:
        st.subheader("Add a New Question")
        with st.form("add_question_form"):
            target_branch = st.text_input("Target Course & Semester (e.g., BCA 2nd Sem)")
            q_text = st.text_area("Question Text")
            
            col_a, col_b = st.columns(2)
            with col_a:
                q_type = st.selectbox("Question Type", ["MCQ", "MSQ", "Numerical"])
            with col_b:
                marks = st.selectbox("Marks", [1, 2], help="MCQ has 25% negative marking. MSQ and Numerical have NO negative marking.")
            
            if q_type == "Numerical":
                q_unit = st.text_input("Unit (Optional - e.g., ns, kg, m/s)")
            else:
                q_unit = ""
                
            options_input = st.text_input("Options (Comma separated for MCQ/MSQ, leave blank for Numerical)")
            correct_input = st.text_input("Correct Answer (For MSQ comma separated, for Numerical enter ONLY number)")
            
            submitted = st.form_submit_button("Add Question", type="primary")
            
            if submitted:
                if not q_text or not correct_input or not target_branch:
                    st.error("Branch, question text, and correct answer are required.")
                else:
                    options = [opt.strip() for opt in options_input.split(",")] if options_input else []
                    is_valid = True
                    
                    if q_type == "MSQ": 
                        correct_ans = [ans.strip() for ans in correct_input.split(",")]
                    elif q_type == "Numerical": 
                        try:
                            correct_ans = float(correct_input)
                        except ValueError:
                            st.error("❌ For Numerical questions, enter ONLY numbers in the answer box.")
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
                            st.toast(f"✅ Question added for {target_branch}!", icon="🎉")
                            time.sleep(0.6)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to add question: {e}")

    # 2. VIEW/EDIT QUESTIONS
    with tab2:
        st.subheader("View & Edit Questions")
        if not existing_branches:
            st.info("No questions available yet.")
        else:
            branch_to_edit = st.selectbox("Select Branch to View/Edit", existing_branches)
            branch_questions = [q for q in questions if q.get("branch", "").lower() == branch_to_edit.lower()]
            
            if not branch_questions:
                st.info("No questions found for this branch.")
            else:
                for idx, q in enumerate(branch_questions):
                    with st.expander(f"Q{idx + 1}: {q['text'][:60]}..."):
                        with st.form(key=f"edit_form_{q['id']}"):
                            edit_q_text = st.text_area("Question Text", value=q['text'])
                            
                            col_a, col_b, col_c = st.columns(3)
                            with col_a:
                                edit_q_type = st.selectbox("Question Type", ["MCQ", "MSQ", "Numerical"], index=["MCQ", "MSQ", "Numerical"].index(q['type']))
                            with col_b:
                                edit_marks = st.selectbox("Marks", [1, 2], index=[1, 2].index(q['marks']))
                            with col_c:
                                edit_unit = st.text_input("Unit", value=q.get('unit', ''))
                            
                            edit_options = st.text_input("Options (Comma separated)", value=",".join(q.get('options') or []))
                            
                            if q['type'] == 'MSQ' and isinstance(q['correct'], list):
                                c_val = ",".join(q['correct'])
                            else:
                                c_val = str(q['correct'])
                                
                            edit_correct = st.text_input("Correct Answer", value=c_val)
                            
                            c1, c2 = st.columns(2)
                            with c1:
                                save_edit = st.form_submit_button("Save Changes", type="primary")
                            with c2:
                                delete_q = st.form_submit_button("Delete Question")
                                
                            if save_edit:
                                is_valid = True
                                if edit_q_type == "MSQ": 
                                    parsed_correct = [ans.strip() for ans in edit_correct.split(",")]
                                elif edit_q_type == "Numerical": 
                                    try:
                                        parsed_correct = float(edit_correct)
                                    except ValueError:
                                        st.error("❌ For Numerical questions, enter ONLY numbers.")
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
                                        st.error(f"Failed to update question: {e}")
                                    
                            if delete_q:
                                try:
                                    delete_question(q['id'])
                                    st.toast("🗑️ Question deleted!", icon="🗑️")
                                    time.sleep(0.6)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Failed to delete question: {e}")

    # 3. QUIZ SETTINGS & PASSKEY
    with tab3:
        st.subheader("Set Time Limits & Quiz Passkeys")
        if not existing_branches:
            st.info("Add questions for a branch first.")
        else:
            branch_for_timer = st.selectbox("Select Branch", existing_branches)
            current_settings = get_branch_settings(branch_for_timer)
            
            with st.form("settings_passkey_form"):
                time_limit = st.number_input(
                    "Time Limit (in minutes, 0 for no limit)", 
                    min_value=0, 
                    value=current_settings.get("time_limit", 30)
                )
                passkey_input = st.text_input(
                    "🔑 Quiz Passkey (Required for students to attempt the quiz)", 
                    value=current_settings.get("passkey", "")
                )
                
                if st.form_submit_button("Save Settings & Passkey", type="primary"):
                    try:
                        save_branch_settings(branch_for_timer, time_limit, passkey_input)
                        st.toast(f"✅ Settings for {branch_for_timer} updated!", icon="🔐")
                        time.sleep(0.6)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to save settings: {e}")
            
            st.divider()
            st.write("📋 **Active Branch Quiz Configurations:**")
            all_cfg = get_all_settings()
            if all_cfg:
                df_cfg = pd.DataFrame(all_cfg)
                st.dataframe(df_cfg, use_container_width=True)

    # 4. VIEW RESULTS & MANAGE
    with tab4:
        st.subheader("Student Leaderboard")
        scores_data = get_all_scores()
        if not scores_data:
            st.info("No students have taken the quiz yet.")
        else:
            results_list = []
            for item in scores_data:
                results_list.append({
                    "Roll No": item["roll_no"],
                    "Name": item["name"],
                    "Branch": item["branch"],
                    "Score": float(item["score"]),
                    "Correct": item.get("correct", 0),
                    "Wrong": item.get("wrong", 0),
                    "Status": item.get("status", "Completed")
                })
            df = pd.DataFrame(results_list)
            branches = sorted(df["Branch"].unique().tolist())
            selected_branch = st.selectbox("Filter by Branch", ["All"] + branches)
            
            if selected_branch != "All":
                df = df[df["Branch"] == selected_branch]
            st.dataframe(df, use_container_width=True)

            st.divider()
            
            st.subheader("Manage Individual Results")
            st.write("Select a student to delete their submission (allowing them to retake the quiz).")
            student_options = [f"{item['roll_no']} - {item['name']} ({item['branch']})" for item in scores_data]
            
            with st.form("delete_student_form"):
                student_to_delete = st.selectbox("Select Student Record", student_options)
                if st.form_submit_button("Delete Student Record"):
                    if student_to_delete:
                        roll_to_delete = student_to_delete.split(" - ")[0]
                        try:
                            delete_student_score(roll_to_delete)
                            st.toast(f"✅ Result for {roll_to_delete} deleted!", icon="🗑️")
                            time.sleep(0.6)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to delete record: {e}")

    # 5. MANAGE DATA
    with tab5:
        st.subheader("Danger Zone")
        if existing_branches:
            branch_to_delete = st.selectbox("Select Branch Quiz to Delete", existing_branches)
            confirm_branch = st.checkbox(f"Confirm deletion for {branch_to_delete}")
            if st.button("🗑️ Delete Branch Quiz"):
                if confirm_branch:
                    try:
                        delete_branch_data(branch_to_delete)
                        st.toast(f"✅ Deleted all data for {branch_to_delete}.", icon="🗑️")
                        time.sleep(0.6)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to delete branch data: {e}")
                else:
                    st.error("Check the confirmation box first.")
        
        st.divider()
        confirm_all = st.checkbox("Confirm Complete Wipe")
        if st.button("🚨 Delete Everything (All Branches)"):
            if confirm_all:
                try:
                    wipe_all_data()
                    st.toast("✅ All data cleared.", icon="🚨")
                    time.sleep(0.6)
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to clear data: {e}")
            else:
                st.error("Check the confirmation box first.")


# --- CANDIDATE DASHBOARD ---
def candidate_dashboard():
    student_branch = st.session_state.student_info['Branch']
    roll_no = st.session_state.user_id
    
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title(f"Quiz: {student_branch}")
        st.caption(f"👤 **{st.session_state.student_info['Name']}** | 🆔 **{roll_no}**")
    with col2:
        st.button("🚪 Logout", on_click=logout, use_container_width=True)
    
    my_questions = get_questions_by_branch(student_branch)
    student_record = get_student_score(roll_no)
    
    # -------------------------------------------------------------
    # IF QUIZ ALREADY SUBMITTED: SHOW RESULT SCREEN & LEADERBOARD
    # -------------------------------------------------------------
    if student_record is not None:
        st.success("🎉 You have successfully completed the quiz!")
        
        st.markdown("### 📊 Your Performance Summary")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Final Score", f"{student_record['score']}")
        m2.metric("Correct Answers", f"{student_record.get('correct', 0)}")
        m3.metric("Wrong Answers", f"{student_record.get('wrong', 0)}")
        m4.metric("Marks Deducted", f"-{student_record.get('deducted', 0.0)}")
        
        st.divider()
        
        st.markdown("### 📝 Review Your Answers")
        saved_responses = student_record.get("responses") or {}
        
        for i, q in enumerate(my_questions):
            with st.container():
                st.markdown("<div class='question-box'>", unsafe_allow_html=True)
                st.markdown(f"**Q{i+1}: {q['text']}** _({q['marks']} Marks)_")
                
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
                    st.warning(f"⚪ **Skipped** | Correct Answer: **{display_correct}**")
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
                        st.success(f"✅ **Correct!** Your Answer: {display_ans}")
                    else:
                        st.error(f"❌ **Wrong.** Your Answer: {display_ans} | Correct Answer: **{display_correct}**")
                
                st.markdown("</div>", unsafe_allow_html=True)

        st.divider()

        st.markdown("### 🏆 Branch Leaderboard")
        branch_scores = get_branch_scores(student_branch)
        if branch_scores:
            df_leaderboard = pd.DataFrame([{"Name": d["name"], "Score": float(d["score"])} for d in branch_scores])
            df_leaderboard.index = df_leaderboard.index + 1
            st.dataframe(df_leaderboard, use_container_width=True)
        return

    # -------------------------------------------------------------
    # TAKING THE QUIZ
    # -------------------------------------------------------------
    if not my_questions:
        st.warning(f"No quiz is currently available for {student_branch}. Please wait for your instructor.")
        return

    st.divider()

    branch_config = get_branch_settings(student_branch)
    time_limit = branch_config.get("time_limit", 30)
    time_expired = False
    
    if time_limit > 0:
        elapsed_seconds = int(time.time() - st.session_state.start_time)
        remaining_seconds = max(0, int((time_limit * 60) - elapsed_seconds))
        
        if remaining_seconds <= 0:
            st.error("⏱️ Your time is up! The quiz is locked.")
            time_expired = True
        else:
            timer_html = f"""
            <div style="
                background-color: #EEF2FF;
                border: 2px solid #4F46E5;
                border-radius: 8px;
                padding: 10px;
                text-align: center;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                font-size: 1.15rem;
                color: #1E1B4B;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            ">
                ⏱️ <b>Time Remaining:</b> 
                <span id="quiz-countdown" style="font-weight: 700; color: #DC2626; font-size: 1.3rem;">--:--</span>
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
                        display.innerText = "00m 00s (Time Expired)";
                        display.style.color = "#991B1B";
                        clearInterval(timerInterval);
                        return;
                    }}
                    display.innerText = formatTime(remaining);
                    remaining--;
                }}

                tick();
                const timerInterval = setInterval(tick, 1000);
            </script>
            """
            components.html(timer_html, height=75)
    
    with st.form("quiz_form"):
        user_answers = {}
        for i, q in enumerate(my_questions):
            st.markdown("<div class='question-box'>", unsafe_allow_html=True)
            
            if q["type"] == "MCQ":
                neg_mark_text = f"-{q['marks'] * 0.25} for wrong"
            else:
                neg_mark_text = "No Negative Marking"
                
            st.markdown(f"**Q{i+1}. {q['text']}** _({q['marks']} Marks | {neg_mark_text})_")
            
            if q["type"] == "MCQ":
                user_answers[i] = st.radio("Options", q.get("options") or [], index=None, key=f"q_{i}", label_visibility="collapsed", disabled=time_expired)
            elif q["type"] == "MSQ":
                user_answers[i] = st.multiselect("Options", q.get("options") or [], key=f"q_{i}", label_visibility="collapsed", disabled=time_expired)
            elif q["type"] == "Numerical":
                col_input, col_unit = st.columns([2, 5])
                with col_input:
                    user_answers[i] = st.text_input("Your answer", key=f"q_{i}", label_visibility="collapsed", disabled=time_expired)
                with col_unit:
                    if q.get("unit"):
                        st.markdown(f"<div style='padding-top:8px;'><b>{q['unit']}</b></div>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
        submit_btn = st.form_submit_button("✅ Submit Final Quiz", type="primary", disabled=time_expired, use_container_width=True)
        
        if submit_btn:
            if time_limit > 0:
                final_elapsed = time.time() - st.session_state.start_time
                if final_elapsed > (time_limit * 60) + 10: 
                    st.error("Submission rejected. You exceeded the time limit.")
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
                        "status": "Rejected (Late)"
                    }
                    try:
                        save_student_score(late_record)
                    except Exception as e:
                        st.error(f"Failed to record submission: {e}")
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
                st.toast("✅ Quiz submitted successfully!", icon="🎉")
                time.sleep(0.6)
                st.rerun()
            except Exception as e:
                st.error(f"Failed to save quiz results: {e}")

def logout():
    st.session_state.logged_in = False
    st.session_state.user_id = ""
    st.session_state.role = ""
    st.session_state.student_info = {}
    st.session_state.start_time = None

# --- APP ROUTING ---
if not st.session_state.logged_in:
    login_screen()
else:
    if st.session_state.role == "admin": 
        admin_dashboard()
    else: 
        candidate_dashboard()
