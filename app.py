# Streamlit Web App to Track Timed Tasks via Browser

import streamlit as st
import pandas as pd
from datetime import datetime

# Updated task data with timings, activity, and notes
initial_data = pd.DataFrame({
    'Time': [
        '07:00–08:00',
        '08:00–09:00',
        '09:00–13:00',
        '13:00–14:00',
        '14:00–18:00',
        '18:00–19:00',
        '19:00–20:00',
        '20:00–21:00',
        '21:00–22:00',
        '22:00 onwards'
    ],
    'Task': [
        'Morning Routine & Exercise',
        'Breakfast & Personal Prep',
        'Work Block 1',
        'Lunch & Short Walk/Break',
        'Work Block 2',
        'Dinner',
        'Learning Block',
        'Free time or wind-down activity',
        'Get ready for bed + light reading',
        'Sleep'
    ],
    'Notes': [
        'Light workout, stretch, or walk',
        'Ease into the day',
        '4-hour work sprint (deep productivity)',
        'Digest + light movement',
        'Admin, lighter tasks',
        'Unwind',
        'Study, reading, or skill-building',
        'Optional screen-free hour',
        'Sleep prep',
        'Aim for 8–9 hours'
    ],
    'Status': [
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False
    ]
})

# Convert string time to datetime for comparison
TIME_FORMAT = "%H:%M"

def parse_time_range(time_range):
    try:
        start_str, end_str = time_range.replace("–", "-").split("-")
        start = datetime.strptime(start_str.strip(), TIME_FORMAT).time()
        end = datetime.strptime(end_str.strip(), TIME_FORMAT).time()
        return start, end
    except:
        return None, None

def is_current_task(start, end):
    now = datetime.now().time()
    return start <= now <= end if start and end else False

# Main App

def main():
    st.set_page_config(page_title="Task Dashboard", layout="wide")
    st.title("🗓️ Full Daily Task Tracker")

    if "data" not in st.session_state:
        st.session_state.data = initial_data.copy()

    df = st.session_state.data

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📋 Timings & Notes")
        updated_status = []
        for i in range(len(df)):
            time_range = df.loc[i, 'Time']
            start, end = parse_time_range(time_range)
            is_current = is_current_task(start, end)
            label = f"{time_range} — {df.loc[i, 'Task']} ({df.loc[i, 'Notes']})"

            if is_current:
                st.markdown(
                    f"""
                    <div style='background-color:#fff8dc; border-left:5px solid #f39c12; padding:12px 16px; margin-bottom:5px; border-radius:6px; font-weight:bold; color:#333;'>
                        ⏰ {label}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            checkbox = st.checkbox(label, value=df.loc[i, 'Status'], key=i)
            updated_status.append(checkbox)

        st.session_state.data['Status'] = updated_status

    with col2:
        st.subheader("📈 Progress Tracker")
        total = len(df)
        completed = sum(updated_status)
        percentage = (completed / total) * 100 if total > 0 else 0
        st.metric(label="🎯 Progress", value=f"{completed}/{total} tasks completed", delta=f"{percentage:.2f}%")
        st.progress(percentage / 100)

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export as CSV",
            data=csv,
            file_name="daily_schedule.csv",
            mime='text/csv'
        )

if __name__ == '__main__':
    main()
