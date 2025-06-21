import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import calendar
import hashlib
import json
import os

# ─────── Configurations ───────
STATE_FILE = "task_state.json"
TZ = pytz.timezone("Asia/Kolkata")
TIME_FORMAT = "%H:%M"

# ─────── Task Templates ───────
weekday_data = pd.DataFrame({
    'Time': [
        '07:00–08:00', '08:00–10:00', '10:00–13:00',
        '13:00–15:00', '15:00–17:30', '17:30–18:00',
        '18:00–20:00', '20:00–21:00', '21:00–22:00',
        '22:00 onwards'
    ],
    'Task': [
        'Morning Routine', 'Breakfast & Personal Prep', 'Work Block 1',
        'Lunch & Short Walk/Break', 'Work Block 2', 'Next Day Planning',
        'Time With Family', 'Workout/Gaming', 'Learning/Gaming', 'Sleep'
    ],
    'Notes': [
        'Light workout, stretch, or walk', 'Ease into the day', '3-hour deep work session',
        'Digest + light movement', 'Focused task completion', 'Prepare for tomorrow',
        'Relax and connect', 'Refresh body or enjoy games', 'Skill-building or game time',
        'Aim for 8–9 hours of sleep'
    ]
})

sunday_data = pd.DataFrame({
    'Time': [
        '08:00–09:00', '09:00–10:00', '10:00–12:00',
        '12:00–14:00', '14:00–16:00', '16:00–18:00',
        '18:00–20:00', '20:00–22:00', '22:00 onwards'
    ],
    'Task': [
        'Lazy Morning', 'Family Breakfast', 'Outdoor Fun/TV Time',
        'Big Lunch + Rest', 'Hobbies/Free Time', 'Light Planning',
        'Movie or Chill Time', 'Prep for Monday', 'Sleep'
    ],
    'Notes': [
        'Wake up slowly', 'Enjoy with family', 'Watch or go outside',
        'Relax post lunch', 'Any personal fun activity', 'Prepare lightly for week',
        'Entertainment time', 'Review goals, clothes ready', 'Full rest'
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
    now = datetime.now(TZ).time()
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
    st.set_page_config(page_title="Solo Leveling Task Tracker", layout="wide")
    st.markdown("""
        <style>
            body {
                background: linear-gradient(to right, #0f0c29, #302b63, #24243e);
                color: #f0f0f0;
            }
            .stButton>button {
                background-color: rgba(0, 255, 255, 0.15);
                color: white;
                border: 1px solid #0ff;
                border-radius: 5px;
            }
            .stButton>button:hover {
                background-color: rgba(0, 255, 255, 0.3);
                color: #000;
            }
        </style>
    """, unsafe_allow_html=True)

    st.title("⚔️ Solo Leveling Daily Quest Tracker")
    today = calendar.day_name[datetime.now(TZ).weekday()]
    df = sunday_data if today == "Sunday" else weekday_data
    task_count = len(df)

    if 'status_list' not in st.session_state or len(st.session_state.status_list) != task_count:
        st.session_state.status_list = load_state(task_count)

    st.success(f"🧭 Current Quest: {get_current_task_label(df)[0]}")
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📝 Daily Quest Log")
        for i in range(task_count):
            label = f"{df.loc[i, 'Time']} — {df.loc[i, 'Task']} ({df.loc[i, 'Notes']})"
            st.session_state.status_list[i] = st.checkbox(label, value=st.session_state.status_list[i], key=f"cb_{i}")

    with col2:
        st.subheader("📈 Progress Board")
        completed = sum(st.session_state.status_list)
        percent = (completed / task_count) * 100
        st.metric("🧮 Progress", f"{completed}/{task_count} quests", delta=f"{percent:.1f}%")
        st.progress(percent / 100)

        csv = df.assign(Status=st.session_state.status_list).to_csv(index=False).encode('utf-8')
        c1, c2 = st.columns(2)
        with c1:
            st.download_button("📤 Export as CSV", data=csv, file_name="quests.csv", mime='text/csv')
        with c2:
            if st.button("♻️ Reset Quests"):
                st.session_state.status_list = [False] * task_count
                save_state(st.session_state.status_list)
                st.rerun()

        st.markdown(f"""
        <div style="background: #141e30; padding: 20px; border-radius: 10px; text-align: center; color: #00ffff; font-size: 18px;">
            ✨ <strong>Daily Buff:</strong> {get_quote_for_date()}
        </div>
        """, unsafe_allow_html=True)

    # ─────── Quest Stats ───────
    with st.expander("📊 Quest Stats (Analytics)", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### ✅ Tasks Completed")
            st.write(f"{completed} out of {task_count} quests cleared.")
            st.write(f"🧮 Progress: **{percent:.1f}%**")

        with col2:
            last_checked_time = None
            for i in reversed(range(task_count)):
                if st.session_state.status_list[i]:
                    last_checked_time = datetime.now(TZ).strftime("%I:%M %p")
                    break

            st.markdown("### 🕒 Last Quest Completion")
            if last_checked_time:
                st.write(f"Last quest checked at: **{last_checked_time}**")
            else:
                st.write("No quests marked yet today.")

    save_state(st.session_state.status_list)

if __name__ == "__main__":
    main()
