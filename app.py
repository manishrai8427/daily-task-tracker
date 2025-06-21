"""
Streamlit Web App – Daily Task Tracker
-------------------------------------
• One single, de‑duplicated file
• Works every day (Sunday included!)
• Always shows Reset, Export CSV, and Motivation
• Robust state handling: pads/truncates saved check‑box list to today’s length
"""

import os
import json
import hashlib
from datetime import datetime

import streamlit as st
import pandas as pd
import pytz
import calendar

# ───────────────────────── Constants & Static Data ──────────────────────────
TZ = pytz.timezone("Asia/Kolkata")  # local timezone
STATE_FILE = "task_state.json"
TIME_FORMAT = "%H:%M"

weekday_data = pd.DataFrame(
    {
        "Time": [
            "07:00–08:00",
            "08:00–10:00",
            "10:00–13:00",
            "13:00–15:00",
            "15:00–17:30",
            "17:30–18:00",
            "18:00–20:00",
            "20:00–21:00",
            "21:00–22:00",
            "22:00 onwards",
        ],
        "Task": [
            "Morning Routine",
            "Breakfast & Personal Prep",
            "Work Block 1",
            "Lunch & Short Walk/Break",
            "Work Block 2",
            "Next Day Planning",
            "Time With Family",
            "Workout/Gaming",
            "Learning/Gaming",
            "Sleep",
        ],
        "Notes": [
            "Light workout, stretch, or walk",
            "Ease into the day",
            "3‑hour deep work session",
            "Digest + light movement",
            "Focused task completion",
            "Prepare for tomorrow",
            "Relax and connect",
            "Refresh body or enjoy games",
            "Skill‑building or game time",
            "Aim for 8–9 hours of sleep",
        ],
    }
)

sunday_data = pd.DataFrame(
    {
        "Time": [
            "08:00–09:00",
            "09:00–10:00",
            "10:00–12:00",
            "12:00–14:00",
            "14:00–16:00",
            "16:00–18:00",
            "18:00–20:00",
            "20:00–22:00",
            "22:00 onwards",
        ],
        "Task": [
            "Lazy Morning",
            "Family Breakfast",
            "Outdoor Fun / TV Time",
            "Big Lunch + Rest",
            "Hobbies / Free Time",
            "Light Planning",
            "Movie or Chill Time",
            "Prep for Monday",
            "Sleep",
        ],
        "Notes": [
            "Wake up slowly",
            "Enjoy with family",
            "Watch or go outside",
            "Relax post lunch",
            "Any personal fun activity",
            "Prepare lightly for week",
            "Entertainment time",
            "Review goals, clothes ready",
            "Full rest",
        ],
    }
)

MOTIVATION_QUOTES = [
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
    "Turn your dreams into plans.",
]

# ───────────────────────────── Helper Functions ─────────────────────────────

def quote_for_today() -> str:
    """Return a deterministic quote for the current date."""
    today_iso = datetime.now(TZ).date().isoformat()
    idx = int(hashlib.sha256(today_iso.encode()).hexdigest(), 16) % len(MOTIVATION_QUOTES)
    return MOTIVATION_QUOTES[idx]


def parse_time_range(rng: str):
    """Return (start_time, end_time) from a string like '07:00-09:00' or '22:00 onwards'."""
    rng = rng.replace("–", "-")  # normalize en‑dash
    if "onwards" in rng:
        start = datetime.strptime(rng.replace(" onwards", "").strip(), TIME_FORMAT).time()
        end = datetime.strptime("23:59", TIME_FORMAT).time()
        return start, end
    if "-" in rng:
        start_str, end_str = rng.split("-")
        return (
            datetime.strptime(start_str.strip(), TIME_FORMAT).time(),
            datetime.strptime(end_str.strip(), TIME_FORMAT).time(),
        )
    return None, None


def current_task_label(df: pd.DataFrame) -> str:
    now_t = datetime.now(TZ).time()
    for _, row in df.iterrows():
        start, end = parse_time_range(row["Time"])
        if start and end and start <= now_t <= end:
            return f"{row['Time']} — {row['Task']}"
    return "No active task currently"


# ──────────────────────── State Load / Save Utilities ────────────────────────

def load_state(task_count: int):
    """Return a list of booleans sized to task_count, padded/truncated as needed."""
    state = [False] * task_count
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                saved = json.load(f).get("status", [])
            state = (saved + [False] * task_count)[:task_count]  # fit size
        except Exception:
            pass  # ignore corrupt file
    return state


def save_state(status_list):
    with open(STATE_FILE, "w") as f:
        json.dump({"status": status_list}, f)


# ──────────────────────────────────── Main ───────────────────────────────────

def main():
    st.set_page_config(page_title="Daily Task Tracker", layout="wide")
    st.title("🗓️ Full Daily Task Tracker")

    is_sunday = calendar.day_name[datetime.now(TZ).weekday()] == "Sunday"
    schedule_df = sunday_data.copy() if is_sunday else weekday_data.copy()
    task_count = len(schedule_df)

    # Ensure session state list has correct length
    if (
        "status_list" not in st.session_state
        or len(st.session_state.status_list) != task_count
    ):
        st.session_state.status_list = load_state(task_count)

    # Current task banner
    st.success(f"✅ Current Task: {current_task_label(schedule_df)}")

    col_tasks, col_side = st.columns([2, 1])

    # ── Task Check‑boxes ────────────────────────────────────────────────────
    with col_tasks:
        st.subheader("📋 Timings & Notes")
        for i, row in schedule_df.iterrows():
            label = f"{row['Time']} — {row['Task']} ({row['Notes']})"
            st.session_state.status_list[i] = st.checkbox(
                label,
                value=st.session_state.status_list[i],
                key=f"checkbox_{i}",
            )

    # ── Sidebar: Progress, Export, Reset, Quote ────────────────────────────
    with col_side:
        st.subheader("📊 Progress Tracker")
        completed = sum(st.session_state.status_list)
        pct = (completed / task_count) * 100 if task_count else 0
        st.metric("🌟 Progress", f"{completed}/{task_count} tasks", delta=f"{pct:.2f}%")
        st.progress(pct / 100)

        # CSV export
        csv_bytes = schedule_df.assign(Status=st.session_state.status_list).to_csv(index=False).encode()
        st.download_button("📄 Export as CSV", data=csv_bytes, file_name="daily_schedule.csv", mime="text/csv")

        # Reset button
        if st.button("🔄 Reset Tasks"):
            st.session_state.status_list = [False] * task_count
            for k in list(st.session_state.keys()):
                if k.startswith("checkbox_"):
                    del st.session_state[k]
            save_state(st.session_state.status_list)
            st.experimental_rerun()

        # Daily motivation card
        st.markdown(
            f"""
            <div style="background:#001d3d;border-radius:8px;padding:20px;margin-top:25px;
                        color:#f0f8ff;font-style:italic;font-size:18px;text-align:center;
                        min-height:130px;display:flex;align-items:center;justify-content:center;">
                🌟 <strong>Daily Motivation:</strong> {quote_for_today()}
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Persist checkbox state once per run
    save_state(st.session_state.status_list)


if __name__ == "__main__":
    main()
