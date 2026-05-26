The app itself is in Python with Streamlit as the front and Supabase as the back

Here’s a concise FAQ you for this app.

***
## Plant Tracker – FAQ
### 1. How do I add a new plant?
- Go to the Overview screen (no plant selected or use the back arrow at the top).
- Scroll to the bottom and click the “Add a new plant” card.
- Fill in:
  - Plant Name (required)
  - Description (optional, supports multiple lines)
  - Location / room (living-room, kitchen, balcony, entryway)
  - Watering frequency (in days)
  - Takes showers (yes/no)
  - Last showered date (if showers are enabled)
- Optionally upload a photo (you can use your phone camera).
- Click “Save Plant”.
### 2. How do I see details for a plant?
- On the Overview screen, each plant is shown as a card with:
  - Location (if set)
  - Name with a colored dot (green/yellow/red for watering status)
  - Last watered date
  - Watering frequency
  - Shower status line
- Click “See details” on a card to open the Plant Details screen for that plant.
### 3. What do the colors on plant names mean?
On the Overview cards:

- 🔴 Red – watering is overdue.
- 🟡 Yellow – watering is due soon or frequency is set but never watered.
- 🟢 Green – watering is on track.

These colors are based on the “Last watered” date plus the watering frequency in days.
### 4. How do I filter plants by room?
- On the Overview screen, use the “Filter by location” dropdown.
- Choose:
  - All
  - living-room
  - kitchen
  - balcony
  - entryway
- The list below will update to show only plants in the selected room.
### 5. How does the shower reminder work?
If “Takes showers” is enabled for a plant:

- From September to May: reminder every 30 days (monthly).
- In June, July, August: reminder every 7 days (weekly).
- The app uses the **Last showered** date (or today if none) to calculate:
  - Shower overdue
  - Shower due soon
  - Shower: next on YYYY-MM-DD

You see this status:
- As a line on the Overview card.
- As a colored message (error/warning/info) on the Plant Details screen.
### 6. How do I edit a plant?
On the Plant Details screen:

- Click “✏️ Edit”.
- You can change:
  - Name
  - Description
  - Location / room (dropdown)
  - Watering frequency (days)
  - Takes showers (yes/no)
  - Last showered date (if showers enabled)
  - Photo (optional replacement)
- Adjust the “Next watering date” if needed.
- Click “💾 Save changes” to store updates.
### 7. How do I update only the watering date?
On the Plant Details screen in view mode:

- Use the “Next watering date” picker to choose the new date.
- Click “✅ Update watering date”.
- The app saves just the `last_watered` date for that plant.
### 8. How do I change the photo for a plant?
- Open the plant’s Details screen.
- Click “✏️ Edit”.
- On the right side, use “Replace photo (optional)” to upload a new image.
- Click “💾 Save changes”.
- The photo will be updated for that plant.
### 9. How do I delete a plant?
On the Plant Details screen:

- In view mode: use the “🗑 Delete” button (third button at the bottom).
- In edit mode: use the “🗑 Delete” button next to “Save changes”.
- You will be asked to confirm by clicking Delete again.
- After deletion:
  - The plant record is removed.
  - Its photo is removed from storage (if possible).
  - You are returned to the Overview screen.
### 10. How do I go back to the plant list?
- Use the back arrow “←” at the top-left.
- This arrow appears on screens other than Overview and returns you to the list of plants.
