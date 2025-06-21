...[unchanged code above]...

        # ─────── Quest Stats ───────
        with st.expander("📊 Quest Stats (Analytics)", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### ✅ Tasks Completed")
                st.write(f"{completed} out of {task_count} quests cleared.")

                percent = (completed / task_count) * 100
                st.write(f"🧮 Progress: **{percent:.1f}%**")

            with col2:
                last_checked_time = None
                for i in reversed(range(task_count)):
                    if st.session_state.status_list[i]:
                        last_checked_time = datetime.now(TZ).strftime("%I:%M %p")
                        break

                if last_checked_time:
                    st.markdown("### 🕒 Last Quest Completion")
                    st.write(f"Last quest checked at: **{last_checked_time}**")
                else:
                    st.markdown("### 🕒 Last Quest Completion")
                    st.write("No quests marked yet today.")

... [unchanged code below] ...
