from datetime import date, datetime

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

if "tasks" not in st.session_state:
    st.session_state.tasks = []
if "schedule_result" not in st.session_state:
    st.session_state.schedule_result = None

st.subheader("Owner and pet")
owner_name = st.text_input("Owner name", value="Jordan", key="owner_name")
owner_preferences = st.text_input(
    "Owner preferences", value="Morning care before work", key="owner_preferences"
)
pet_name = st.text_input("Pet name", value="Mochi", key="pet_name")
species = st.selectbox("Species", ["dog", "cat", "other"], key="pet_species")
care_notes = st.text_input("Pet care notes", key="care_notes")

owner = Owner(name=owner_name, preferences=owner_preferences)
pet = Pet(name=pet_name, species=species, care_notes=care_notes)
owner.add_pet(pet)
for saved_task in st.session_state.tasks:
    owner.add_task(saved_task)
    pet.add_task(saved_task)

st.subheader("Care tasks")
with st.form("add_task_form", clear_on_submit=True):
    task_title = st.text_input("Task title", placeholder="Morning walk")
    duration_column, priority_column = st.columns(2)
    with duration_column:
        task_duration = st.number_input(
            "Duration (minutes)", min_value=1, max_value=240, value=20
        )
    with priority_column:
        task_priority = st.selectbox("Priority", ["high", "medium", "low"])
    add_task = st.form_submit_button("Add task")

if add_task:
    if task_title.strip():
        st.session_state.tasks.append(
            Task(
                title=task_title.strip(),
                duration_minutes=int(task_duration),
                priority=task_priority,
            )
        )
        st.session_state.schedule_result = None
    else:
        st.error("Enter a task title before adding it.")

if st.session_state.tasks:
    st.dataframe(
        [
            {
                "Task": task.title,
                "Duration (min)": task.duration_minutes,
                "Priority": task.priority.title(),
            }
            for task in st.session_state.tasks
        ],
        hide_index=True,
        use_container_width=True,
    )
    if st.button("Clear all tasks"):
        st.session_state.tasks = []
        st.session_state.schedule_result = None
else:
    st.info("No tasks yet. Add a care task above to get started.")

st.subheader("Daily schedule")
start_time = st.time_input(
    "Start time", value=datetime.strptime("08:00", "%H:%M").time()
)
available_minutes = st.number_input(
    "Available time (minutes)", min_value=1, max_value=1440, value=60
)

if st.button(
    "Generate schedule", type="primary", disabled=not st.session_state.tasks
):
    plan_start = datetime.combine(date.today(), start_time)
    st.session_state.schedule_result = Scheduler().schedule_tasks(
        st.session_state.tasks,
        start_time=plan_start,
        available_minutes=int(available_minutes),
    )

result = st.session_state.schedule_result
if result is not None:
    scheduled_tasks, skipped_tasks, explanations = result
    st.markdown(f"### Daily plan for {pet.name} ({pet.species})")
    st.caption(
        f"Prepared for {owner.name} · {start_time:%H:%M} · "
        f"{int(available_minutes)} minutes"
    )

    st.markdown("#### Scheduled tasks")
    if scheduled_tasks:
        for task in scheduled_tasks:
            st.write(
                f"**{task.scheduled_start:%H:%M}–{task.scheduled_end:%H:%M}** "
                f"{task.title} · {task.duration_minutes} min · "
                f"{task.priority.title()} priority"
            )
    else:
        st.info("No tasks fit in the available time.")

    st.markdown("#### Skipped tasks")
    if skipped_tasks:
        for task in skipped_tasks:
            st.write(f"{task.title} · {task.duration_minutes} min")
    else:
        st.write("None")

    st.markdown("#### Explanations")
    for explanation in explanations:
        st.write(f"- {explanation}")