import streamlit as st
import json
import os
import pandas as pd
import time

# --- PAGE CONFIGURATION & STYLING ---
st.set_page_config(page_title="Pro Quiz Portal", page_icon="🎓", layout="centered")

# Custom CSS to make the app look attractive
st.markdown("""
<style>
    /* Main container styling */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #1E3A8A;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Style the tabs */
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
    
    /* Metric Cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        color: #1E3A8A;
    }
    
    /* Question Card Styling */
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

# --- DATABASE CONFIGURATION ---
DATA_FILE = "quiz_data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"questions": [], "scores": {}, "settings": {}}
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
        if "settings" not in data:
            data["settings"] = {}
        return data

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

db = load_data()

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
    
    tab1, tab2 = st.tabs(["👨‍🎓 Student Entry", "👨‍🏫 Admin Login"])
    
    with tab1:
        st.subheader("Enter your details to start")
        with st.form("student_login_form"):
            name = st.text_input("Full Name")
            rollno = st.text_input("Roll Number")
            section = st.text_input("Section")
            branch = st.text_input("Course & Semester (e.g., BCA 2nd Sem)")
            
            submit_student = st.form_submit_button("🚀 Start Quiz", type="primary", use_container_width=True)
            
            if submit_student:
                if name and rollno and section and branch:
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
                else:
                    st.error("Please fill in all details.")
                    
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
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["➕ Create Question", "✏️ View/Edit", "⏱️ Settings", "📊 Results", "🗑️ Manage Data"])
    
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
            correct_input = st.text_input("Correct Answer (For numerical, enter ONLY the number)")
            
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
                            st.error("❌ For Numerical questions, enter ONLY numbers in the answer box. Use the 'Unit' box above for 'ns'.")
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
                        db["questions"].append(new_question)
                        save_data(db)
                        st.success(f"✅ Question added for {target_branch}!")

    # 2. VIEW/EDIT QUESTIONS
    with tab2:
        st.subheader("View & Edit Questions")
        existing_branches = list(set([q.get("branch", "") for q in db["questions"] if q.get("branch")]))
        
        if not existing_branches:
            st.info("No questions available yet.")
        else:
            branch_to_edit = st.selectbox("Select Branch to View/Edit", existing_branches)
            branch_questions = [(idx, q) for idx, q in enumerate(db["questions"]) if q.get("branch") == branch_to_edit]
            
            if not branch_questions:
                st.info("No questions found for this branch.")
            else:
                for idx_in_list, (original_idx, q) in enumerate(branch_questions):
                    with st.expander(f"Q{idx_in_list + 1}: {q['text'][:60]}..."):
                        with st.form(key=f"edit_form_{original_idx}"):
                            edit_q_text = st.text_area("Question Text", value=q['text'])
                            
                            col_a, col_b, col_c = st.columns(3)
                            with col_a:
                                edit_q_type = st.selectbox("Question Type", ["MCQ", "MSQ", "Numerical"], index=["MCQ", "MSQ", "Numerical"].index(q['type']))
                            with col_b:
                                edit_marks = st.selectbox("Marks", [1, 2], index=[1, 2].index(q['marks']))
                            with col_c:
                                edit_unit = st.text_input("Unit", value=q.get('unit', ''))
                            
                            edit_options = st.text_input("Options (Comma separated)", value=",".join(q.get('options', [])))
                            
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
                                    db["questions"][original_idx]["text"] = edit_q_text
                                    db["questions"][original_idx]["type"] = edit_q_type
                                    db["questions"][original_idx]["marks"] = edit_marks
                                    db["questions"][original_idx]["options"] = [opt.strip() for opt in edit_options.split(",")] if edit_options else []
                                    db["questions"][original_idx]["correct"] = parsed_correct
                                    db["questions"][original_idx]["unit"] = edit_unit.strip()
                                    save_data(db)
                                    st.success("✅ Question updated successfully!")
                                    st.rerun()
                                
                            if delete_q:
                                db["questions"].pop(original_idx)
                                save_data(db)
                                st.success("🗑️ Question deleted!")
                                st.rerun()

    # 3. QUIZ SETTINGS
    with tab3:
        st.subheader("Set Time Limits")
        existing_branches = list(set([q.get("branch", "") for q in db["questions"] if q.get("branch")]))
        if not existing_branches:
            st.info("Add questions for a branch first.")
        else:
            with st.form("timer_form"):
                branch_for_timer = st.selectbox("Select Branch", existing_branches)
                time_limit = st.number_input("Time Limit (in minutes, 0 for no limit)", min_value=0, value=30)
                if st.form_submit_button("Save Time Limit", type="primary"):
                    db["settings"][branch_for_timer] = time_limit
                    save_data(db)
                    st.success(f"✅ Time limit for {branch_for_timer} set to {time_limit} minutes.")

    # 4. VIEW RESULTS & MANAGE
    with tab4:
        st.subheader("Student Leaderboard")
        if not db["scores"]:
            st.info("No students have taken the quiz yet.")
        else:
            results_list = []
            # Extract top-level details for dataframe
            for uid, data in db["scores"].items():
                results_list.append({
                    "Roll No": uid,
                    "Name": data["Name"],
                    "Branch": data["Branch"],
                    "Score": data["Score"],
                    "Correct": data.get("Correct", 0),
                    "Wrong": data.get("Wrong", 0)
                })
            df = pd.DataFrame(results_list)
            branches = df["Branch"].unique().tolist()
            selected_branch = st.selectbox("Filter by Branch", ["All"] + branches)
            
            if selected_branch != "All":
                df = df[df["Branch"] == selected_branch]
            st.dataframe(df, use_container_width=True)

            st.divider()
            
            st.subheader("Manage Individual Results")
            st.write("Select a student to delete their submission (allowing them to retake the quiz).")
            student_options = [f"{uid} - {data['Name']} ({data['Branch']})" for uid, data in db["scores"].items()]
            
            with st.form("delete_student_form"):
                student_to_delete = st.selectbox("Select Student Record", student_options)
                if st.form_submit_button("Delete Student Record"):
                    if student_to_delete:
                        roll_to_delete = student_to_delete.split(" - ")[0]
                        if roll_to_delete in db["scores"]:
                            del db["scores"][roll_to_delete]
                            save_data(db)
                            st.success(f"✅ Result for {roll_to_delete} deleted successfully!")
                            st.rerun()

    # 5. MANAGE DATA
    with tab5:
        st.subheader("Danger Zone")
        existing_branches = list(set([q.get("branch", "") for q in db["questions"] if q.get("branch")]))
        if existing_branches:
            branch_to_delete = st.selectbox("Select Branch Quiz to Delete", existing_branches)
            confirm_branch = st.checkbox(f"Confirm deletion for {branch_to_delete}")
            if st.button("🗑️ Delete Branch Quiz"):
                if confirm_branch:
                    db["questions"] = [q for q in db["questions"] if q.get("branch") != branch_to_delete]
                    db["scores"] = {k: v for k, v in db["scores"].items() if v["Branch"] != branch_to_delete}
                    if branch_to_delete in db["settings"]: del db["settings"][branch_to_delete]
                    save_data(db)
                    st.success(f"✅ Deleted all data for {branch_to_delete}.")
                    st.rerun()
                else:
                    st.error("Check the confirmation box first.")
        
        st.divider()
        confirm_all = st.checkbox("Confirm Complete Wipe")
        if st.button("🚨 Delete Everything (All Branches)"):
            if confirm_all:
                db["questions"] = []
                db["scores"] = {}
                db["settings"] = {}
                save_data(db)
                st.success("✅ All data cleared.")
                st.rerun()
            else:
                st.error("Check the confirmation box first.")

# --- CANDIDATE DASHBOARD ---
def candidate_dashboard():
    student_branch = st.session_state.student_info['Branch']
    
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title(f"Quiz: {student_branch}")
        st.caption(f"👤 **{st.session_state.student_info['Name']}** | 🆔 **{st.session_state.user_id}**")
    with col2:
        st.button("🚪 Logout", on_click=logout, use_container_width=True)
    
    # FETCH QUESTIONS
    my_questions = [q for q in db["questions"] if q.get("branch", "").lower() == student_branch.lower()]
    
    # -------------------------------------------------------------
    # IF QUIZ ALREADY SUBMITTED: SHOW RESULT SCREEN & LEADERBOARD
    # -------------------------------------------------------------
    if st.session_state.user_id in db["scores"]:
        student_data = db["scores"][st.session_state.user_id]
        
        st.success("🎉 You have successfully completed the quiz!")
        
        # 1. Performance Summary Metrics
        st.markdown("### 📊 Your Performance Summary")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Final Score", f"{student_data['Score']}")
        m2.metric("Correct Answers", f"{student_data.get('Correct', 0)}")
        m3.metric("Wrong Answers", f"{student_data.get('Wrong', 0)}")
        m4.metric("Marks Deducted", f"-{student_data.get('Deducted', 0.0)}")
        
        st.divider()
        
        # 2. Detailed Review
        st.markdown("### 📝 Review Your Answers")
        saved_responses = student_data.get("Responses", {})
        
        for i, q in enumerate(my_questions):
            with st.container():
                st.markdown(f"<div class='question-box'>", unsafe_allow_html=True)
                st.markdown(f"**Q{i+1}: {q['text']}** _({q['marks']} Marks)_")
                
                # Fetch what the user answered
                ans = saved_responses.get(str(i), None)
                
                # Format answers for readability
                display_ans = ans
                display_correct = q['correct']
                if q["type"] == "MSQ":
                    display_ans = ", ".join(ans) if ans else "None"
                    display_correct = ", ".join(q['correct'])
                elif q["type"] == "Numerical":
                    if ans == "": display_ans = "None"
                    if q.get("unit"): 
                        if ans != "": display_ans = f"{ans} {q['unit']}"
                        display_correct = f"{q['correct']} {q['unit']}"
                
                # Evaluate correctly for the UI box
                if ans is None or ans == [] or ans == "":
                    st.warning(f"⚪ **Skipped** | Correct Answer: **{display_correct}**")
                else:
                    is_correct = False
                    if q["type"] == "MCQ": is_correct = (ans == q["correct"])
                    elif q["type"] == "MSQ": is_correct = set(ans) == set(q["correct"])
                    elif q["type"] == "Numerical":
                        try: is_correct = (float(ans) == float(q["correct"]))
                        except ValueError: is_correct = False

                    if is_correct:
                        st.success(f"✅ **Correct!** Your Answer: {display_ans}")
                    else:
                        st.error(f"❌ **Wrong.** Your Answer: {display_ans} | Correct Answer: **{display_correct}**")
                
                st.markdown("</div>", unsafe_allow_html=True)

        st.divider()

        # 3. Branch Leaderboard
        st.markdown("### 🏆 Branch Leaderboard")
        branch_scores = []
        for uid, data in db["scores"].items():
            if data.get("Branch", "").lower() == student_branch.lower():
                branch_scores.append({"Name": data["Name"], "Score": data["Score"]})
        if branch_scores:
            df_leaderboard = pd.DataFrame(branch_scores)
            df_leaderboard = df_leaderboard.sort_values(by="Score", ascending=False).reset_index(drop=True)
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

    time_limit = db.get("settings", {}).get(student_branch, 0)
    time_expired = False
    
    if time_limit > 0:
        elapsed_seconds = time.time() - st.session_state.start_time
        remaining_seconds = (time_limit * 60) - elapsed_seconds
        
        if remaining_seconds <= 0:
            st.error("⏱️ Your time is up! The quiz is locked.")
            time_expired = True
        else:
            mins = int(remaining_seconds // 60)
            secs = int(remaining_seconds % 60)
            st.info(f"⏱️ **Time Limit:** {time_limit} minutes. You have roughly **{mins} min {secs} sec** remaining.")
    
    with st.form("quiz_form"):
        user_answers = {}
        for i, q in enumerate(my_questions):
            st.markdown(f"<div class='question-box'>", unsafe_allow_html=True)
            
            # Display Negative Marking hints correctly
            if q["type"] == "MCQ":
                neg_mark_text = f"-{q['marks'] * 0.25} for wrong"
            else:
                neg_mark_text = "No Negative Marking"
                
            st.markdown(f"**Q{i+1}. {q['text']}** _({q['marks']} Marks | {neg_mark_text})_")
            
            if q["type"] == "MCQ":
                user_answers[i] = st.radio("Options", q["options"], index=None, key=f"q_{i}", label_visibility="collapsed", disabled=time_expired)
            elif q["type"] == "MSQ":
                user_answers[i] = st.multiselect("Options", q["options"], key=f"q_{i}", label_visibility="collapsed", disabled=time_expired)
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
                    db["scores"][st.session_state.user_id] = {
                        "Name": st.session_state.student_info["Name"],
                        "Roll No": st.session_state.student_info["Roll No"],
                        "Section": st.session_state.student_info["Section"],
                        "Branch": student_branch,
                        "Score": 0,
                        "Status": "Rejected (Late)",
                        "Responses": {}
                    }
                    save_data(db)
                    st.rerun()
                    return

            # SCORING ENGINE
            score = 0.0
            correct_count = 0
            wrong_count = 0
            total_deducted = 0.0
            saved_responses = {}
            
            for i, q in enumerate(my_questions):
                ans = user_answers[i]
                marks = q["marks"]
                saved_responses[str(i)] = ans # Save what the user typed/clicked
                
                if ans is None or ans == [] or ans == "": 
                    continue # Skipped question
                    
                is_correct = False
                if q["type"] == "MCQ": is_correct = (ans == q["correct"])
                elif q["type"] == "MSQ": is_correct = set(ans) == set(q["correct"])
                elif q["type"] == "Numerical":
                    try: is_correct = (float(ans) == float(q["correct"]))
                    except ValueError: is_correct = False

                if is_correct: 
                    score += marks
                    correct_count += 1
                else: 
                    wrong_count += 1
                    # NEGATIVE MARKING ONLY FOR MCQ NOW
                    if q["type"] == "MCQ":
                        penalty = (marks * 0.25)
                        score -= penalty
                        total_deducted += penalty

            # Save detailed metrics to DB
            db["scores"][st.session_state.user_id] = {
                "Name": st.session_state.student_info["Name"],
                "Roll No": st.session_state.student_info["Roll No"],
                "Section": st.session_state.student_info["Section"],
                "Branch": student_branch,
                "Score": score,
                "Correct": correct_count,
                "Wrong": wrong_count,
                "Deducted": total_deducted,
                "Responses": saved_responses,
                "Status": "Completed"
            }
            save_data(db)
            st.rerun()

def logout():
    st.session_state.logged_in = False
    st.session_state.user_id = ""
    st.session_state.role = ""
    st.session_state.student_info = {}
    st.session_state.start_time = None

if not st.session_state.logged_in:
    login_screen()
else:
    if st.session_state.role == "admin": admin_dashboard()
    else: candidate_dashboard()
