"""Streamlit app for citizens to report and track garbage collection complaints."""

import logging

import requests
import streamlit as st

from backend.config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

st.set_page_config(page_title="JanMitra AI - Citizen", page_icon="🗑️")
st.title("🗑️ Report a Garbage Complaint")

CITIZEN_ID = settings.HARDCODED_CITIZEN_ID
language_options = settings.SUPPORTED_LANGUAGES

language_code = st.selectbox(
    "Choose your language",
    options=list(language_options.keys()),
    format_func=lambda code: language_options[code]["name"],
)

input_mode = st.radio("How would you like to report the complaint?", ["Speak", "Type"])

audio_bytes: bytes | None = None
text_value: str | None = None

if input_mode == "Speak":
    recording = st.audio_input("Record your complaint")
    if recording is not None:
        audio_bytes = recording.getvalue()
else:
    text_value = st.text_area("Describe the problem", placeholder="e.g. Garbage not collected near my house for 3 days")

photo = st.file_uploader("Attach a photo (optional)", type=["jpg", "jpeg", "png"])

if st.button("Submit Complaint", type="primary"):
    if not audio_bytes and not (text_value and text_value.strip()):
        st.error("Please record or type your complaint before submitting.")
    else:
        files = {}
        if audio_bytes:
            files["audio"] = ("complaint.wav", audio_bytes, "audio/wav")
        if photo is not None:
            files["photo"] = (photo.name, photo.getvalue(), photo.type)

        data = {"citizen_id": CITIZEN_ID, "language": language_code}
        if text_value:
            data["text"] = text_value

        try:
            response = requests.post(
                f"{settings.BACKEND_URL}/complaints", data=data, files=files or None, timeout=60
            )
            if response.status_code == 200:
                st.success("Complaint submitted successfully!")
                logger.info("Complaint submitted by %s", CITIZEN_ID)
            else:
                detail = response.json().get("detail", response.text)
                st.error(f"Could not submit complaint: {detail}")
                logger.error("Complaint submission failed: %s", detail)
        except requests.RequestException as exc:
            st.error("Could not reach the server. Please try again.")
            logger.error("Request to backend failed: %s", exc, exc_info=True)

st.divider()
st.subheader("Your Complaints")

if st.button("🔄 Refresh"):
    st.rerun()

try:
    response = requests.get(
        f"{settings.BACKEND_URL}/complaints", params={"lang": language_code}, timeout=30
    )
    response.raise_for_status()
    complaints = [c for c in response.json() if c["citizen_id"] == CITIZEN_ID]

    if not complaints:
        st.info("You haven't submitted any complaints yet.")

    for complaint in complaints:
        status_label = "✅ Resolved" if complaint["status"] == "resolved" else "🟡 Open"
        with st.container(border=True):
            st.markdown(f"**{status_label}** — {complaint['created_at']}")
            st.write(complaint["display_text"])
            if complaint["photo_path"]:
                st.image(f"{settings.BACKEND_URL}/uploads/{complaint['photo_path']}", width=200)
except requests.RequestException as exc:
    st.error("Could not load your complaints. Please try again.")
    logger.error("Failed to fetch complaints: %s", exc, exc_info=True)
