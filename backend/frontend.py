from langdetect import detect
import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000"

for key, default in {
    "user": None,
    "chats": [],
    "active_chat": None,
    "search_results": [],
    "search_answer": "",
    "show_auth_modal": False,
    "auth_mode": "login",
    "sending": False,
    "search_text": "",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

def handle_login():
    username = st.session_state.auth_username
    password = st.session_state.auth_password
    try:
        resp = requests.post(f"{API_URL}/login", json={"username": username, "password": password})
        resp.raise_for_status()
        st.session_state.user = resp.json()
        st.session_state.show_auth_modal = False
        st.success("✅ Logged in successfully!")
    except requests.exceptions.HTTPError:
        st.error(resp.json().get("detail", "Login failed"))

def handle_register():
    username = st.session_state.auth_username
    password = st.session_state.auth_password
    try:
        resp = requests.post(f"{API_URL}/register", json={"username": username, "password": password})
        resp.raise_for_status()
        st.session_state.user = resp.json()
        st.session_state.show_auth_modal = False
        st.success("✅ Registered and logged in!")
    except requests.exceptions.HTTPError:
        st.error(resp.json().get("detail", "Registration failed"))

def handle_logout():
    st.session_state.user = None
    st.session_state.chats = []
    st.session_state.active_chat = None
    st.session_state.search_answer = ""
    st.session_state.search_results = []
    st.success("You have been logged out.")

def handle_send(search_text):
    if not search_text.strip():
        return
    st.session_state.sending = True
    try:
        lang = detect(search_text)
        if lang not in ["en", "mk"]:
            lang = "mk" # Default to Macedonian if undetected
        st.session_state.query_lang = lang
        user_id = st.session_state.user["id"] if st.session_state.user else None
        payload = {"query": search_text, "top_k": 10, "user_id": user_id}
        res = requests.post(f"{API_URL}/search", json=payload)
        if res.status_code == 200:
            data = res.json()
            st.session_state.search_answer = data["answer"]
            st.session_state.search_results = data["retrieved_cars"]
        else:
            st.error(f"Search failed ({res.status_code})")
    except requests.exceptions.RequestException:
        st.error("Failed to connect to API")
    finally:
        st.session_state.sending = False

col1, col2 = st.columns([8, 2])
with col2:
    if st.session_state.user:
        st.write(f"{st.session_state.user['username']}")
        st.button("Logout", on_click=handle_logout)
    else:
        st.button("Login / Register", on_click=lambda: st.session_state.update(show_auth_modal=True, auth_mode="login"))

if st.session_state.show_auth_modal:
    with st.expander("Authentication", expanded=True):
        mode = st.radio(
            "Choose action",
            ["Login", "Register"],
            index=0 if st.session_state.auth_mode == "login" else 1,
        )
        st.session_state.auth_mode = mode.lower()
        username = st.text_input("Username", key="auth_username")
        password = st.text_input("Password", type="password", key="auth_password")
        if mode == "Login":
            st.button("Login", key="login_submit", on_click=handle_login)
        else:
            st.button("Register", key="register_submit", on_click=handle_register)

st.sidebar.title("Chats")
if st.session_state.user:
    user_id = st.session_state.user["id"]
    res = requests.get(f"{API_URL}/chat/{user_id}")
    if res.status_code == 200:
        st.session_state.chats = [c for c in res.json() if c['message'].strip() != ""]
    st.sidebar.subheader("Chat History")
    for c in st.session_state.chats:
        if st.sidebar.button(c['title'], key=f"chat_{c['id']}"):
            st.session_state.active_chat = c['id']
            st.session_state.search_answer = c.get("answer", "")
            st.session_state.search_results = []
    if st.sidebar.button("New Chat"):
        st.session_state.active_chat = None
        st.session_state.search_answer = ""
        st.session_state.search_results = []
else:
    st.sidebar.write("Temporary chats")

search_input = st.text_input("Type your search here/Побарај што се нуди на пазарот", key="search_text")
st.button(
    "Send",
    disabled=st.session_state.sending or not search_input.strip(),
    on_click=handle_send,
    args=(search_input,)
)

if st.session_state.active_chat and st.session_state.user:
    st.subheader("Chat Messages")
    for c in st.session_state.chats:
        if c['id'] == st.session_state.active_chat:
            st.write(f"{c['message']}")
            if c.get("answer"):
                st.write(f"{c['answer']}")

if st.session_state.search_answer:
    if st.session_state.get("query_lang") == "mk":
        st.subheader("Резиме / Најдобар автомобил")
    else:
        st.subheader("Summary / Best Car")
    st.write(st.session_state.search_answer)

if st.session_state.search_results:
    if st.session_state.get("query_lang") == "mk":
        st.subheader("Топ 10 Огласи")
    else:
        st.subheader("Top 10 Listings")

    for r in st.session_state.search_results:
        meta = r["metadata"]

        st.markdown(f"### [{meta.get('title','N/A')}]({meta.get('url','')})")

        if st.session_state.get("query_lang") == "mk":
            st.write(f"**Цена:** {meta.get('price','N/A')} € | **Километража:** {meta.get('mileage','N/A')} км | **Датум на објава:** {meta.get('date_posted','N/A')}")
        else:
            st.write(f"**Price:** {meta.get('price','N/A')} € | **Mileage:** {meta.get('mileage','N/A')} km | **Date Posted:** {meta.get('date_posted','N/A')}")

        if meta.get("image_url"):
            st.image(meta["image_url"], width=300)

        st.markdown("---")

