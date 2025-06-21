# Streamlit Web App to Track Timed Tasks via Browser

import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import calendar
import hashlib
import json
import os

# Define persistent file name
STATE_FILE = "task_state.json"

# Define weekday and Sunday task schedules
weekday_data = pd.DataFrame({
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
    ]
})

sunday_data = pd.DataFrame({
    'Time': [
        '08:00–09:00',
        '09:00–10:00',
        '10:00–12:00',
        '12:00–14:00',
        '14:00–16:00',
        '16:00–18:00',
        '18:00–20:00',
        '20:00–22:00',
        '22:00 onwards'
    ],
    'Task': [
        'Lazy Morning',
        'Family Breakfast',
        'Outdoor Fun/TV Time',
        'Big Lunch + Rest',
        'Hobbies/Free Time',
        'Light Planning',
        'Movie or Chill Time',
        'Prep for Monday',
        'Sleep'
    ],
    'Notes': [
        'Wake up slowly',
        'Enjoy with family',
        'Watch or go outside',
        'Relax post lunch',
        'Any personal fun activity',
        'Prepare lightly for week',
        'Entertainment time',
        'Review goals, clothes ready',
        'Full rest'
    ]
})

motivation_quotes_list = [
    "Every day is a new beginning.",
    "Your potential is endless.",
    "Do something today your future self will thank you for.",
    "Small steps every day.",
    "Dream big. Start small. Act now.",
    "You’ve got what it takes.",
    "Wake up with determination. Go to bed with satisfaction.",
    "You are stronger than you think.",
    "The key to success is to focus on goals, not obstacles.",
    "Push through. You are doing great.",
    "Consistency is more important than perfection.",
    "Every moment is a fresh beginning.",
    "You are your only limit.",
    "Stay focused and never give up.",
    "Turn your dreams into plans."
]

def get_quote_for_date():
    date_hash = int(hashlib.sha256(datetime.now().date().isoformat().encode()).hexdigest(), 16)
    return motivation_quotes_list[date_hash % len(motivation_quotes_list)]

TIME_FORMAT = "%H:%M"

def parse_time_range(time_range):
    try:
        time_range = time_range.replace("–", "-")
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
    except:
        return None, None

def get_current_task_label(df):
    now = datetime.now(pytz.timezone("Asia/Kolkata")).time()
    for i in range(len(df)):
        start, end = parse_time_range(df.loc[i, 'Time'])
        if start and end and start <= now <= end:
            return f"{df.loc[i, 'Time']} — {df.loc[i, 'Task']}", i
    return "No active task currently", None

def load_state(task_count):
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            state = json.load(f)
            return state.get("status", [False] * task_count)
    return [False] * task_count

def save_state(status_list):
    with open(STATE_FILE, "w") as f:
        json.dump({"status": status_list}, f)

def main():
    st.set_page_config(page_title="Task Dashboard", layout="wide")
    st.title("🗓️ Full Daily Task Tracker")

    today_name = calendar.day_name[datetime.now(pytz.timezone("Asia/Kolkata")).weekday()]
    selected_data = sunday_data.copy() if today_name == "Sunday" else weekday_data.copy()
    task_count = len(selected_data)

    current_task_label, current_index = get_current_task_label(selected_data)
    st.success(f"✅ Current Task: {current_task_label}")

    if 'status_list' not in st.session_state:
        st.session_state.status_list = load_state(task_count)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📋 Timings & Notes")
        for i in range(task_count):
            label = f"{selected_data.loc[i, 'Time']} — {selected_data.loc[i, 'Task']} ({selected_data.loc[i, 'Notes']})"
            checkbox_key = f"checkbox_{i}"
            checked = st.checkbox(label, value=st.session_state.status_list[i], key=checkbox_key)
            st.session_state.status_list[i] = checked
        save_state(st.session_state.status_list)

    with col2:
        st.subheader("📊 Progress Tracker")
        completed = sum(st.session_state.status_list)
        percentage = (completed / task_count) * 100 if task_count > 0 else 0
        st.metric(label="🌟 Progress", value=f"{completed}/{task_count} tasks completed", delta=f"{percentage:.2f}%")
        st.progress(percentage / 100)

        csv = selected_data.assign(Status=st.session_state.status_list).to_csv(index=False).encode('utf-8')
        colA, colB = st.columns(2)
        with colA:
            st.download_button("📄 Export as CSV", data=csv, file_name="daily_schedule.csv", mime='text/csv')
        with colB:
            if st.button("🔄 Reset Tasks"):
                st.session_state.status_list = [False] * task_count
                save_state(st.session_state.status_list)
                st.experimental_rerun()

        st.markdown(f"""
        <div style="background-color: #001d3d; border-radius: 8px; padding: 20px; margin-top: 25px; color: #f0f8ff; font-style: italic; font-size: 18px; text-align: center; min-height: 130px; display: flex; align-items: center; justify-content: center;">
            🌟 <strong>Daily Motivation:</strong> {get_quote_for_date()}
        </div>
        """, unsafe_allow_html=True)

if __name__ == '__main__':
    main()
