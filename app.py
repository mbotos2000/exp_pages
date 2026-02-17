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

name, user = require_login("🔐 App Login")
st.title("Dashboard")
st.success(f"Welcome, {name}!")





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
    st.page_link("pages/exp1.py")
with c2:
    st.page_link("pages/exp2.py")


