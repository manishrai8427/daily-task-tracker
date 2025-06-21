# Streamlit Web App to Track Timed Tasks via Browser

import streamlit as st
import pandas as pd
from datetime import datetime
import pytz  # Using pytz for timezone support
import os
import pickle

# File to store persistent data
SAVE_FILE = "task_status.pkl"

# Updated task data with timings, activity, and notes
initial_data = pd.DataFrame({
    'Time': [
        '07:00–08:00',
        '08:00–10:00',
        '10:00–13:00',
        '13:00–15:00',
        '15:00–17:30',
        '17:30–18:00',
        '18:00–20:00',
        '20:00–21:00',
        '21:00–22:00',
        '22:00 onwards'
    ],
    'Task': [
        'Morning Routine',
        'Breakfast & Personal Prep',
        'Work Block 1',
        'Lunch & Short Walk/Break',
        'Work Block 2',
        'Next Day Planning',
        'Time With Family',
        'Workout/Gaming',
        'Learning/Gaming',
        'Sleep'
    ],
    'Notes': [
        'Light workout, stretch, or walk',
        'Ease into the day',
        '3-hour deep work session',
        'Digest + light movement',
        'Focused task completion',
        'Prepare for tomorrow',
        'Relax and connect',
        'Refresh body or enjoy games',
        'Skill-building or game time',
        'Aim for 8–9 hours of sleep'
    ],
    'Status': [False]*10
})

TIME_FORMAT = "%H:%M"

def parse_time_range(time_range):
    try:
        time_range = time_range.replace("–", "-")  # normalize en-dash
        if "onwards" in time_range:
            start_str = time_range.replace(" onwards", "").strip()
            start = datetime.strptime(start_str, TIME_FORMAT).time()
            return start, datetime.strptime("23:59", TIME_FORMAT).time()

        if "-" in time_range:
            start_str, end_str = time_range.split("-")
        else:
            return None, None

        start = datetime.strptime(start_str.strip(), TIME_FORMAT).time()
        end = datetime.strptime(end_str.strip(), TIME_FORMAT).time()
        return start, end
    except Exception as e:
        print("Time parsing error:", e)
        return None, None

def get_current_task_label(df):
    now = datetime.now(pytz.timezone("Asia/Kolkata")).time()
    for i in range(len(df)):
        start, end = parse_time_range(df.loc[i, 'Time'])
        if start and end and start <= now <= end:
            return f"{df.loc[i, 'Time']} — {df.loc[i, 'Task']}", i
    return "No active task currently", None

def is_current_task(start, end):
    now = datetime.now(pytz.timezone("Asia/Kolkata")).time()
    return start <= now <= end if start and end else False

def load_saved_data():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, 'rb') as f:
            return pickle.load(f)
    return initial_data.copy()

def save_data(df):
    with open(SAVE_FILE, 'wb') as f:
        pickle.dump(df, f)

# ⚠️ Delete saved file once to apply new data
if os.path.exists(SAVE_FILE):
    os.remove(SAVE_FILE)

def main():
    st.set_page_config(page_title="Task Dashboard", layout="wide")
    st.title("🗓️ Full Daily Task Tracker")

    if "data" not in st.session_state:
        st.session_state.data = load_saved_data()

    if st.session_state.get("reset_flag", False):
        st.session_state.reset_flag = False
        st.session_state.data = initial_data.copy(deep=True)
        for key in list(st.session_state.keys()):
            if key.startswith("checkbox_"):
                del st.session_state[key]
        save_data(st.session_state.data)
        st.rerun()

    df = st.session_state.data

    # Display current task only
    current_task_label, current_index = get_current_task_label(df)
    col_task = st.container()
    with col_task:
        st.success(f"✅ Current Task: {current_task_label}")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📋 Timings & Notes")
        updated_status = []
        for i in range(len(df)):
            time_range = df.loc[i, 'Time']
            start, end = parse_time_range(time_range)
            is_current = (i == current_index)
            label = f"{time_range} — {df.loc[i, 'Task']} ({df.loc[i, 'Notes']})"

            checkbox_key = f"checkbox_{i}"
            default_value = st.session_state.get(checkbox_key, df.loc[i, 'Status'])
            checkbox = st.checkbox(label, value=default_value, key=checkbox_key)
            updated_status.append(checkbox)

            if is_current:
                st.markdown(
                    f"""
                    <div style='background-color:#fff8dc; border-left:5px solid #f39c12; padding:12px 16px; margin-bottom:5px; border-radius:6px; font-weight:bold; color:#333;'>
                        ⏰ {label}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        df['Status'] = updated_status
        save_data(df)

    with col2:
        st.subheader("📊 Progress Tracker")
        total = len(df)
        completed = sum(updated_status)
        percentage = (completed / total) * 100 if total > 0 else 0
        st.metric(label="🌟 Progress", value=f"{completed}/{total} tasks completed", delta=f"{percentage:.2f}%")
        st.progress(percentage / 100)

        csv = df.to_csv(index=False).encode('utf-8')

        colA, colB = st.columns(2)
        with colA:
            st.download_button(
                label="📄 Export as CSV",
                data=csv,
                file_name="daily_schedule.csv",
                mime='text/csv'
            )
        with colB:
            if st.button("🔄 Reset Tasks"):
                st.session_state.reset_flag = True
                st.rerun()

if __name__ == '__main__':
    main()
