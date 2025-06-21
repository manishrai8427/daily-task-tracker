import os
import json
import hashlib
from datetime import datetime
import calendar

import streamlit as st
import pandas as pd
import pytz

# ───────── Config ─────────
TZ = pytz.timezone("Asia/Kolkata")
STATE_FILE = "task_state.json"
TIME_FORMAT = "%H:%M"

# ───────── Schedule Data ─────────
weekday_data = pd.DataFrame({
    "Time": [
        "07:00–08:00", "08:00–10:00", "10:00–13:00", "13:00–15:00",
        "15:00–17:30", "17:30–18:00", "18:00–20:00", "20:00–21:00",
        "21:00–22:00", "22:00 onwards",
    ],
    "Task": [
        "Morning Routine", "Breakfast & Personal Prep", "Work Block 1",
        "Lunch & Short Walk/Break", "Work Block 2", "Next Day Planning",
        "Time With Family", "Workout/Gaming", "Learning/Gaming", "Sleep",
    ],
    "Notes": [
        "Light workout, stretch, or walk", "Ease into the day",
        "3-hour deep work session", "Digest + light movement",
        "Focused task completion", "Prepare for tomorrow", "Relax and connect",
        "Refresh body / enjoy games", "Skill‑building or game time",
        "Aim for 8‑9 hours of sleep",
    ],
})

sunday_data = pd.DataFrame({
    "Time": [
        "08:00–09:00", "09:00–10:00", "10:00–12:00", "12:00–14:00",
        "14:00–16:00", "16:00–18:00", "18:00–20:00", "20:00–22:00",
        "22:00 onwards",
    ],
    "Task": [
        "Lazy Morning", "Family Breakfast", "Outdoor Fun / TV Time",
        "Big Lunch + Rest", "Hobbies / Free Time", "Light Planning",
        "Movie or Chill Time", "Prep for Monday", "Sleep",
    ],
    "Notes": [
        "Wake up slowly", "Enjoy with family", "Watch or go outside",
        "Relax post lunch", "Any personal fun activity",
        "Prepare lightly for week", "Entertainment time",
        "Review goals, clothes ready", "Full rest",
    ],
})

MOTIVATION_QUOTES = [
    "Every day is a new beginning.", "Your potential is endless.",
    "Do something today your future self will thank you for.", "Small steps every day.",
    "Dream big. Start small. Act now.", "You’ve got what it takes.",
    "Wake up with determination. Go to bed with satisfaction.", "You are stronger than you think.",
    "Focus on goals, not obstacles.", "Push through. You are doing great.",
    "Consistency beats perfection.", "Every moment is a fresh start.",
    "You are your only limit.", "Stay focused and never give up.",
    "Turn your dreams into plans."
]

# ───────── Utility Functions ─────────
def quote_for_today():
    today_iso = datetime.now(TZ).date().isoformat()
    idx = int(hashlib.sha256(today_iso.encode()).hexdigest(), 16) % len(MOTIVATION_QUOTES)
    return MOTIVATION_QUOTES[idx]

def parse_time_range(rng):
    rng = rng.replace("–", "-")
    if "onwards" in rng:
        start = datetime.strptime(rng.replace(" onwards", "").strip(), TIME_FORMAT).time()
        end = datetime.strptime("23:59", TIME_FORMAT).time()
        return start, end
    if "-" in rng:
        start_str, end_str = rng.split("-")
        return (
            datetime.strptime(start_str.strip(), TIME_FORMAT).time(),
            datetime.strptime(end_str.strip(), TIME_FORMAT).time()
        )
    return None, None

def current_task_label(df):
    now_t = datetime.now(TZ).time()
    for _, row in df.iterrows():
        start, end = parse_time_range(row["Time"])
        if start and end and start <= now_t <= end:
            return f"{row['Time']} — {row['Task']}"
    return "No active task currently"

# ───────── Persistence ─────────
def load_state(task_count):
    if not os.path.exists(STATE_FILE):
        return [False] * task_count
    try:
        with open(STATE_FILE, "r") as f:
            saved = json.load(f).get("status", [])
        return (saved + [False] * task_count)[:task_count]
    except Exception:
        return [False] * task_count

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump({"status": state}, f)

# ───────── Main App ─────────
def main():
    st.set_page_config(page_title="Daily Task Tracker", layout="wide")

    is_sunday = calendar.day_name[datetime.now(TZ).weekday()] == "Sunday"
    schedule_df = sunday_data if is_sunday else weekday_data
    task_count = len(schedule_df)
    ref_rows = len(weekday_data)

    if "status_list" not in st.session_state or len(st.session_state.status_list) != task_count:
        st.session_state.status_list = load_state(task_count)

    st.title("🗓️ Full Daily Task Tracker")
    st.success(f"✅ Current Task: {current_task_label(schedule_df)}")

    col_tasks, col_side = st.columns([2, 1])

    with col_tasks:
        st.subheader("📋 Timings & Notes")
        for i, row in schedule_df.iterrows():
            label = f"{row['Time']} — {row['Task']} ({row['Notes']})"
            checked = st.checkbox(label, value=st.session_state.status_list[i], key=f"cb_{i}")
            st.session_state.status_list[i] = checked
        for _ in range(ref_rows - task_count):
            st.write(" ")

    with col_side:
        st.subheader("📊 Progress Tracker")
        completed = sum(st.session_state.status_list)
        percent = (completed / task_count) * 100
        st.metric("🌟 Progress", f"{completed}/{task_count} tasks completed", delta=f"{percent:.1f}%")
        st.progress(percent / 100)

        csv_data = schedule_df.assign(Status=st.session_state.status_list).to_csv(index=False).encode("utf-8")
        colA, colB = st.columns(2)
        with colA:
            st.download_button("📄 Export as CSV", data=csv_data, file_name="daily_schedule.csv", mime="text/csv")
        with colB:
            def reset_tasks():
                """Clear all check‑boxes safely and rerun."""
                # Remove widget states for every checkbox
                for key in list(st.session_state.keys()):
                    if key.startswith("cb_"):
                        del st.session_state[key]
                # Reset master list and persist
                st.session_state.status_list = [False] * task_count
                save_state(st.session_state.status_list)
                st.experimental_rerun()

            st.button("🔄 Reset Tasks", on_click=reset_tasks)

        st.markdown(
            f"""
            <div style='background:#001d3d;border-radius:8px;padding:20px;margin-top:25px;
                        color:#f0f8ff;font-style:italic;font-size:18px;text-align:center;
                        min-height:120px;display:flex;align-items:center;justify-content:center;'>
                🌟 <strong>Daily Motivation:</strong> {quote_for_today()}
            </div>
            """,
            unsafe_allow_html=True
        )

    save_state(st.session_state.status_list)

if __name__ == "__main__":
    main()
