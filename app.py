import streamlit as st

from pawpal_system import Owner, Pet, CareTask, ScheduleManager

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# --- Session state (the "vault") ---------------------------------------------
# Streamlit reruns this script top-to-bottom on every interaction, so we store
# a single Owner in st.session_state. Pets, their tasks, and the scheduler all
# hang off this one object, giving us a single source of truth that persists
# across reruns.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Default Owner")

owner = st.session_state.owner

with st.expander("Scenario", expanded=False):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.
"""
    )

st.divider()

# --- Owner settings ----------------------------------------------------------
st.subheader("👤 Owner")
with st.form("owner_form"):
    name = st.text_input("Owner name", value=owner.name)
    hours = st.number_input(
        "Available hours today",
        min_value=0.0,
        max_value=24.0,
        value=float(owner.available_hours),
        step=0.5,
    )
    if st.form_submit_button("Save owner"):
        owner.update_profile(name, hours)
        st.success(f"Saved. {owner.available_minutes} minutes available today.")

st.divider()

# --- Add a pet ---------------------------------------------------------------
st.subheader("🐕 Add a pet")
with st.form("pet_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        pet_name = st.text_input("Pet name", value="")
    with col2:
        species = st.selectbox("Species", ["dog", "cat", "other"])
    with col3:
        age = st.number_input("Age", min_value=0, max_value=50, value=1)
    if st.form_submit_button("Add pet"):
        if pet_name.strip():
            owner.add_pet(Pet(pet_name.strip(), species, int(age)))
            st.success(f"Added {pet_name.strip()}.")
        else:
            st.warning("Please enter a pet name.")

st.divider()

# --- Add a task --------------------------------------------------------------
st.subheader("📋 Add a task")
if not owner.pets:
    st.info("Add a pet first — tasks belong to a pet.")
else:
    with st.form("task_form", clear_on_submit=True):
        selected_name = st.selectbox(
            "For which pet?",
            options=[p.name for p in owner.pets],
        )
        pet_choice = next(p for p in owner.pets if p.name == selected_name)
        col1, col2 = st.columns(2)
        with col1:
            task_title = st.text_input("Task title", value="Morning walk")
            duration = st.number_input(
                "Duration (minutes)", min_value=1, max_value=240, value=20
            )
        with col2:
            frequency = st.selectbox("Frequency", ["daily", "weekly", "monthly"])
            priority = st.selectbox("Priority", ["high", "medium", "low"])
        if st.form_submit_button("Add task"):
            if task_title.strip():
                pet_choice.add_task(
                    CareTask(task_title.strip(), int(duration), frequency, priority)
                )
                st.success(f"Added '{task_title.strip()}' to {pet_choice.name}.")
            else:
                st.warning("Please enter a task title.")

st.divider()

# --- Current pets & tasks ----------------------------------------------------
# Rendered after the forms above, so any change made this run (Streamlit reruns
# on every submit) is already reflected here.
st.subheader("🏠 Current pets & tasks")
if not owner.pets:
    st.info("No pets yet.")
else:
    for pet in owner.pets:
        st.markdown(f"**{pet.get_profile_summary()}**")
        if not pet.tasks:
            st.caption("No tasks yet.")
        else:
            for task in pet.tasks:
                done = "✅" if task.is_completed else "⬜"
                st.write(
                    f"{done} {task.title} — {task.duration} min "
                    f"[{task.priority}, {task.frequency}]"
                )

st.divider()

# --- Generate schedule -------------------------------------------------------
st.subheader("🗓️ Build Schedule")
if st.button("Generate schedule"):
    if not owner.all_tasks():
        st.warning("No tasks to schedule yet. Add a pet and some tasks first.")
    elif owner.available_minutes <= 0:
        st.warning("Set the owner's available hours above so there's time to plan.")
    else:
        owner.schedule.generate_daily_schedule(owner)
        st.markdown("#### Today's Schedule")
        st.text(owner.schedule.get_schedule_explanation())
