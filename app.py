from __future__ import print_function
from io import BytesIO
from datetime import *
import streamlit as st
import pandas as pd
from pandas import *
from docx2python import docx2python
import os
import base64
import time
import ftplib
from mailmerge import MailMerge
from difflib import get_close_matches
import pickle
import string
from auth_simple import require_login
import hashlib
import time

def _hash(pwd: str) -> str:
    return hashlib.sha256(pwd.encode("utf-8")).hexdigest()

def _get_users():
    try:
        return st.secrets["users"]
    except Exception:
        return {}

def require_login(title="Login"):
    st.title(title)
    if "auth" not in st.session_state:
        st.session_state.auth = {"ok": False, "user": None, "name": None, "time": None}

    if st.session_state.auth["ok"]:
        with st.sidebar:
            if st.button("Logout"):
                st.session_state.auth = {"ok": False, "user": None, "name": None, "time": None}
                st.rerun()
        return st.session_state.auth["name"], st.session_state.auth["user"]

    users = _get_users()
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        if u in users and _hash(p) == users[u]["hash"]:
            st.session_state.auth = {"ok": True, "user": u, "name": users[u]["name"], "time": time.time()}
            st.rerun()
        else:
            st.error("Invalid username or password")
            st.stop()

    st.stop()

name, user = require_login("🔐 App Login")
st.title("Dashboard")
st.success(f"Welcome, {name}!")


st.set_page_config(
    page_title="My Multipage App",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Sidebar / Branding ---
with st.sidebar:
    st.image("assets/logo.png", width=160, caption="Company")
    st.markdown("---")
    st.write("Navigate using the sidebar pages.")
    st.markdown(
        """
        **Quick links**
        - ./Upload_CSV
        - ./Dashboard
        """
    )

# --- Home content ---
st.title("🧭 Welcome")
st.write(
    """
    This is the **Home** page of a multi‑page Streamlit app.

    Use the **sidebar** to switch between pages:
    - **Upload CSV**: upload and preview a dataset.
    - **Dashboard**: view a simple summary of your data.

    Data you upload is kept in `st.session_state` so it’s available across pages.
    """
)


c1, c2, c3 = st.columns([1, 1, 4])
with c1:
    st.page_link("pages/1_📤_Upload_CSV.py", label="Go to Upload CSV", icon="📤")
with c2:
    st.page_link("pages/2_📊_Dashboard.py", label="Go to Dashboard", icon="📊")

st.info("Tip: You can also navigate using the sidebar.")


