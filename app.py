import streamlit as st
from datetime import datetime
from PIL import Image
import io
from supabase import create_client, Client
from datetime import datetime, date, timedelta


# Load logo
logo = Image.open("logo.png")

# ---------- Page config ----------
st.set_page_config(
    page_title="Plant Tracker",
    page_icon=logo,      # use your logo here
    layout="wide",
)

# ---------- Supabase config ----------
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
BUCKET = "plant-photos"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------- UI state (no sidebar) ----------
if "selected_id" not in st.session_state:
    st.session_state.selected_id = None
if "mode" not in st.session_state:
    st.session_state.mode = "view"
if "page" not in st.session_state:
    st.session_state.page = "Overview"

page = st.session_state.page



# Top navigation buttons
top_col1, top_col2 = st.columns([1, 1])

with top_col1:
    # Only show back button when NOT on Overview
    if st.session_state.page != "Overview":
        if st.button("←", key="back_to_list", width="content"):
            st.session_state.page = "Overview"
            st.session_state.selected_id = None
            st.session_state.mode = "view"
            st.rerun()



page = st.session_state.page



######################################################

plants = (
    supabase.table("plants")
    .select("id, name, description, last_watered, photo_path, watering_frequency_days")
    .order("name")
    .execute()
).data



#-----------------------------------------------------------------------------
# ----------------- OVERVIEW PAGE -----------------
#-----------------------------------------------------------------------------

if st.session_state.page == "Overview":
    st.header("🏠🌱🌸🌼")
    st.subheader("My Plants")

    if not plants:
        st.info("No plants yet. Add your first plant below.")
    else:
        for p in plants:
            plant_id = p["id"]
            name = p.get("name", "No name")
            last = p.get("last_watered") or "Never"
            photo_path = p.get("photo_path")
            freq = p.get("watering_frequency_days")

            # --- watering status ---
            status_label = ""
            status_color = ""

            if last and freq:
                try:
                    last_dt = datetime.strptime(last, "%Y-%m-%d").date()
                    next_due = last_dt + timedelta(days=freq)
                    today = date.today()
                
                    if today > next_due:
                        status_label = "Overdue for watering"
                        status_color = "red"
                    elif (next_due - today).days <= 1:
                        status_label = "Due soon"
                        status_color = "orange"

                except Exception:
                    pass # if parsing fails, just keep status

            elif freq:
                status_label = "Set frequency but never watered"
                status_color = "orange"
            
            last_display = last or "Never"



            with st.form(key=f"plant_form_{plant_id}"):
                col_img, col_text = st.columns([1, 3])

                with col_img:
                    if photo_path:
                        img_url = supabase.storage.from_(BUCKET).get_public_url(photo_path)
                        st.image(img_url, width=60)
                    else:
                        st.write("🪴")

                with col_text:
                    # Highlight name if overdue/due
                    if status_color == "red":
                        st.markdown(f"**🔴 {name}**")
                    elif status_color == "orange":
                        st.markdown(f"**🟠 {name}**")
                    else:
                        st.markdown(f"**{name}**")

                    st.write(f"Last watered: {last_display}")

                    if freq:
                        st.caption(f"Every {freq} days")

                    if status_label:
                        st.caption(status_label)
                    

                submitted = st.form_submit_button("See details", use_container_width=True)

            if submitted:
                st.session_state.page = "Plant Details"
                st.session_state.selected_id = plant_id
                st.session_state.mode = "view"
                st.rerun()

    # Add plant card only on Overview
    with st.form(key="add_plant_card"):
        col_img, col_text = st.columns([1, 3])

        with col_img:
            st.write("➕")

        with col_text:
            st.markdown("**Add plant**")
            
        add_clicked = st.form_submit_button("Create a new plant entry", use_container_width=True)

    if add_clicked:
        st.session_state.page = "Add Plant"
        st.session_state.selected_id = None
        st.session_state.mode = "view"
        st.rerun()





#-----------------------------------------------------------------------------
# ---------- Add Plant ----------
#-----------------------------------------------------------------------------
elif page == "Add Plant":
    st.header("➕ Add New Plant")

    name = st.text_input("Plant Name")
    description = st.text_area("Description", height=100)
    watering_frequency_days = st.number_input(
    "Watering frequency (days)",
    min_value=1,
    max_value=365,
    value=7,
    step=1,
)

    uploaded_file = st.file_uploader(
        "📸 Take/upload photo (you can use phone camera)",
        type=["jpg", "jpeg", "png"],
    )

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Preview", use_column_width=True)

    if st.button("💾 Save Plant", use_container_width=True):
        if not name:
            st.error("Name is required.")
        else:
            photo_path = None

            if uploaded_file is not None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                ext = uploaded_file.name.split(".")[-1].lower()
                safe_name = name.lower().replace(" ", "_")
                photo_path = f"{safe_name}_{timestamp}.{ext}"

                try:
                    file_bytes = uploaded_file.getvalue()
                    res = supabase.storage.from_(BUCKET).upload(
                        photo_path,
                        file_bytes,
                    )
                    st.caption(f"DEBUG upload add: {res}")
                except Exception as e:
                    st.error(f"Photo upload failed: {e}")
                    photo_path = None

            try:
                data = {
                    "name": name,
                    "description": description,
                    "photo_path": photo_path,
                    "watering_frequency_days": int(watering_frequency_days) if watering_frequency_days else None,
                }
                supabase.table("plants").insert(data).execute()
                st.success("🌱 Plant added!")
                st.rerun()
            except Exception as e:
                st.error(f"Error saving plant: {e}")

    st.info("💡 Tip: On mobile, choose 'Camera' when uploading a photo.")






#-----------------------------------------------------------------------------
# ---------- Plant Details ----------
#-----------------------------------------------------------------------------
elif st.session_state.page == "Plant Details":
    st.header("📋 Plant Details")

    # Debug info – you can remove later
    #st.caption(f"DEBUG: selected_id={st.session_state.selected_id}")

    if st.session_state.selected_id is None:
        st.warning("👈 Select a plant on the 'Overview' page first.")
        st.stop()

    # Fetch plant by ID
    try:
        response = (
            supabase.table("plants")
            .select("*")
            .eq("id", st.session_state.selected_id)
            .execute()
        )
        rows = response.data or []
    except Exception as e:
        st.error(f"Error loading plant details: {e}")
        rows = []

    if not rows:
        st.error("Plant not found.")
        st.stop()

    plant = rows[0]
    mode = st.session_state.get("mode", "view")

    col1, col2 = st.columns(2)

    # ----- LEFT: text fields -----
    with col1:
        if mode == "edit":
            new_name = st.text_input("Name", value=plant["name"])
            new_desc = st.text_area(
                "Description", value=plant.get("description") or "", height=100
            )
            new_freq = st.number_input(
                "Watering frequency (days)",
                min_value=1,
                max_value=365,
                value=plant.get("watering_frequency_days") or 7,
                step=1,
            )
        else:
            st.subheader(plant["name"])
            st.write(f"**Description:** {plant.get('description') or 'No description'}")
            freq = plant.get("watering_frequency_days")
            st.write(
                f"**Watering frequency:** {freq} days" if freq else "**Watering frequency:** not set"
            )

        st.write(f"**Last watered:** {plant.get('last_watered') or 'Never'}")

    # ----- RIGHT: photo -----
    with col2:
        photo_path = plant.get("photo_path")
        if photo_path:
            # Construct public URL directly
            photo_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{photo_path}"
            st.image(photo_url, 
                     width=400,          # target ~400x400 display size
                    clamp=True,         # better contrast handling
                    )
        else:
            st.write("❌ No photo.")

        new_file = None
        if mode == "edit":
            new_file = st.file_uploader(
                "Replace photo (optional)",
                type=["jpg", "jpeg", "png"],
                key="edit_photo",
            )

    # ----- Watering date -----
    new_date = st.date_input(
        "Next watering date",
        value=datetime.now().date(),
    )

        # ----- Buttons row -----
    colA, colB, colC, colD = st.columns(4)

    # Edit button (switch to edit mode)
    with colA:
        if st.button("✏️ Edit", use_container_width=True):
            st.session_state.mode = "edit"
            st.rerun()

    # Save changes (edit mode)
    with colB:
        if mode == "edit":
            if st.button("💾 Save Changes", use_container_width=True):
                updates = {
                    "name": new_name,
                    "description": new_desc,
                    "last_watered": str(new_date),
                    "watering_frequency_days": int(new_freq) if new_freq else None,
                }
                if new_file is not None:
                    from datetime import datetime as dt

                    ext = new_file.name.split(".")[-1].lower()
                    safe_name = new_name.lower().replace(" ", "_")
                    photo_path_new = f"{safe_name}_{dt.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
                    supabase.storage.from_(BUCKET).upload(
                        photo_path_new,
                        new_file.read(),
                    )
                    updates["photo_path"] = photo_path_new

                supabase.table("plants").update(updates).eq(
                    "id", plant["id"]
                ).execute()
                st.success("Changes saved!")
                st.session_state.mode = "view"
                st.rerun()

    # Update watering only (view mode)
    with colC:
        if mode == "view":
            if st.button("✅ Update Watering Date", use_container_width=True):
                supabase.table("plants").update(
                    {"last_watered": str(new_date)}
                ).eq("id", plant["id"]).execute()
                st.success("Watering date updated!")
                st.rerun()