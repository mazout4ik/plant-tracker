import streamlit as st
from datetime import datetime
from PIL import Image
import io
from supabase import create_client, Client

# ---------- Page config ----------
st.set_page_config(page_title="Plant Tracker", layout="wide")

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
col_nav1, col_nav2 = st.columns(2)
with col_nav1:
    if st.button("🏠 Overview", use_container_width=True):
        st.session_state.page = "Overview"
        st.rerun()
with col_nav2:
    if st.button("➕ Add Plant", use_container_width=True):
        st.session_state.page = "Add Plant"
        st.rerun()

page = st.session_state.page

# ---------- Overview ----------
if page == "Overview":
    st.header("🏠 All Plants")

    try:
        response = (
            supabase.table("plants")
            .select("id, name, last_watered")
            .order("name")
            .execute()
        )
        plants = response.data or []
    except Exception as e:
        st.error(f"Error loading plants: {e}")
        plants = []

    if not plants:
        st.info("No plants yet. Add one on the 'Add Plant' page.")
    else:
        for p in plants:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                if st.button(
                    f"{p['name']} - Last watered: {p['last_watered'] or 'Never'}",
                    key=f"name_{p['id']}",
                ):
                    st.session_state.selected_id = p["id"]
                    st.session_state.mode = "view"
                    st.session_state.page = "Plant Details"
                    st.rerun()
            with col2:
                if st.button("Edit", key=f"edit_{p['id']}"):
                    st.session_state.selected_id = p["id"]
                    st.session_state.mode = "edit"
                    st.session_state.page = "Plant Details"
                    st.rerun()
            with col3:
                if st.button("Delete", key=f"del_{p['id']}"):
                    supabase.table("plants").delete().eq("id", p["id"]).execute()
                    st.success(f"Deleted {p['name']}")
                    st.rerun()

# ---------- Add Plant ----------
elif page == "Add Plant":
    st.header("➕ Add New Plant")

    name = st.text_input("Plant Name")
    description = st.text_area("Description", height=100)

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
                }
                supabase.table("plants").insert(data).execute()
                st.success("🌱 Plant added!")
                st.rerun()
            except Exception as e:
                st.error(f"Error saving plant: {e}")

    st.info("💡 Tip: On mobile, choose 'Camera' when uploading a photo.")




# ---------- Plant Details ----------
elif st.session_state.page == "Plant Details":
    st.header("📋 Plant Details")

    # Debug info – you can remove later
    st.caption(f"DEBUG: selected_id={st.session_state.selected_id}")

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
        else:
            st.subheader(plant["name"])
            st.write(f"**Description:** {plant.get('description') or 'No description'}")

        st.write(f"**Last watered:** {plant.get('last_watered') or 'Never'}")

    # ----- RIGHT: photo -----
    with col2:
        photo_path = plant.get("photo_path")
        if photo_path:
            try:
                public_url_data = supabase.storage.from_(BUCKET).get_public_url(
                    photo_path
                )
                if isinstance(public_url_data, dict) and "publicUrl" in public_url_data:
                    photo_url = public_url_data["publicUrl"]
                elif hasattr(public_url_data, "data") and isinstance(
                    public_url_data.data, dict
                ):
                    photo_url = public_url_data.data.get("publicUrl")
                else:
                    photo_url = None

                if photo_url:
                    st.image(photo_url, use_column_width=True)
                else:
                    st.write("Photo URL not available.")
            except Exception as e:
                st.error(f"Error loading photo: {e}")
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
    colA, colB, colC = st.columns(3)

    # Save changes (edit mode)
    with colA:
        if mode == "edit":
            if st.button("💾 Save Changes", use_container_width=True):
                updates = {
                    "name": new_name,
                    "description": new_desc,
                    "last_watered": str(new_date),
                }
                if new_file is not None:
                    from datetime import datetime as dt

                    ext = new_file.name.split(".")[-1].lower()
                    safe_name = new_name.lower().replace(" ", "_")
                    photo_path_new = f"{safe_name}_{dt.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
                    file_bytes = new_file.getvalue()
                    try:
                        res = supabase.storage.from_(BUCKET).upload(
                            photo_path_new,
                            file_bytes,
                        )
                        st.caption(f"DEBUG upload edit: {res}")
                        updates["photo_path"] = photo_path_new
                    except Exception as e:
                        st.error(f"Photo upload failed: {e}")

                supabase.table("plants").update(updates).eq(
                    "id", plant["id"]
                ).execute()
                st.success("Changes saved!")
                st.session_state.mode = "view"
                st.rerun()

    # Update watering only (view mode)
    with colB:
        if mode == "view":
            if st.button("✅ Update Watering Date", use_container_width=True):
                supabase.table("plants").update(
                    {"last_watered": str(new_date)}
                ).eq("id", plant["id"]).execute()
                st.success("Watering date updated!")
                st.rerun()

    # Back button
    with colC:
        if st.button("← Back to Overview", use_container_width=True):
            st.session_state.selected_id = None
            st.session_state.mode = "view"
            st.session_state.page = "Overview"
            st.rerun()