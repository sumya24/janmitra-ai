"""Streamlit app for the (single, hardcoded) worker to view and resolve complaints."""

import logging
import sys
from pathlib import Path

import requests
import streamlit as st

# Ensure the project root is importable regardless of how this script is launched
# (e.g. plain `streamlit run frontend/worker_app.py` does not add it automatically).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.config import settings  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

st.set_page_config(page_title="JanMitra AI - Worker", page_icon="🧹")
st.title("🧹 Worker Dashboard")
st.caption(f"Logged in as {settings.HARDCODED_WORKER_ID}")

language_options = settings.SUPPORTED_LANGUAGES
language_code = st.selectbox(
    "View complaints in",
    options=list(language_options.keys()),
    format_func=lambda code: language_options[code]["name"],
)

if st.button("🔄 Refresh"):
    st.rerun()


def _mark_resolved(complaint_id: int) -> None:
    """Send a PATCH request to mark a complaint as resolved."""
    try:
        response = requests.patch(
            f"{settings.BACKEND_URL}/complaints/{complaint_id}",
            json={"status": "resolved"},
            timeout=30,
        )
        if response.status_code == 200:
            st.success(f"Complaint #{complaint_id} marked as resolved.")
            logger.info("Complaint %s marked resolved by %s", complaint_id, settings.HARDCODED_WORKER_ID)
        else:
            detail = response.json().get("detail", response.text)
            st.error(f"Could not update complaint: {detail}")
    except requests.RequestException as exc:
        st.error("Could not reach the server. Please try again.")
        logger.error("Status update request failed: %s", exc, exc_info=True)


try:
    response = requests.get(
        f"{settings.BACKEND_URL}/complaints", params={"lang": language_code}, timeout=30
    )
    response.raise_for_status()
    complaints = response.json()

    if not complaints:
        st.info("No complaints have been reported yet.")

    for complaint in complaints:
        status_label = "✅ Resolved" if complaint["status"] == "resolved" else "🟡 Open"
        with st.container(border=True):
            st.markdown(f"**Complaint #{complaint['id']}** — {status_label} — {complaint['created_at']}")
            st.markdown(f"**Summary:** {complaint['summary']}")
            st.write(complaint["display_text"])
            if complaint["photo_path"]:
                st.image(f"{settings.BACKEND_URL}/uploads/{complaint['photo_path']}", width=200)
            if complaint["status"] == "open":
                st.button(
                    "Mark Resolved",
                    key=f"resolve_{complaint['id']}",
                    on_click=_mark_resolved,
                    args=(complaint["id"],),
                )
except requests.RequestException as exc:
    st.error("Could not load complaints. Please try again.")
    logger.error("Failed to fetch complaints: %s", exc, exc_info=True)
