# auth_simple.py
import streamlit as st
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
