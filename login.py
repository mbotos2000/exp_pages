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
