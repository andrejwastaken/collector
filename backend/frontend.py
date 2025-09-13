import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

# --- Session state ---
if "user" not in st.session_state:
    st.session_state.user = None
if "chats" not in st.session_state:
    st.session_state.chats = []
if "search_results" not in st.session_state:
    st.session_state.search_results = []
if "search_answer" not in st.session_state:
    st.session_state.search_answer = ""

# --- Sidebar: login/register ---
st.sidebar.title("Login/Register")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Login"):
    res = requests.post(f"{API_URL}/login", json={"username": username, "password": password})
    if res.status_code == 200:
        st.session_state.user = res.json()
        st.success(f"Logged in as {username}")
    else:
        st.error("Invalid credentials")

if st.sidebar.button("Register"):
    res = requests.post(f"{API_URL}/register", json={"username": username, "password": password})
    if res.status_code == 200:
        st.success("Registered! You can now login.")
    else:
        st.error(res.json()["detail"])

# --- Sidebar: Chat history ---
st.sidebar.subheader("Chat History")
if st.session_state.user:
    user_id = st.session_state.user["id"]
    res = requests.get(f"{API_URL}/chat/{user_id}")
    if res.status_code == 200:
        st.session_state.chats = res.json()
    st.text_input("Search chats")
    st.write("- New Chat")
    for c in st.session_state.chats:
        st.write(f"- {c['message'][:30]}...")

# --- Main page ---
st.title("Search Me")
st.write("Your personal car search assistant.")

# --- Search input ---
search_text = st.text_input("Type your search here (e.g., 'Cheapest car in Skopje')")

if st.button("Search"):
    if search_text:
        payload = {"query": search_text, "top_k": 10}
        res = requests.post(f"{API_URL}/search", json=payload)
        if res.status_code == 200:
            data = res.json()
            st.session_state.search_answer = data["answer"]
            st.session_state.search_results = data["retrieved_cars"]
        else:
            st.error("Search failed")

# --- Display LLM answer ---
if st.session_state.search_answer:
    st.subheader("Answer")
    st.write(st.session_state.search_answer)

# --- Display retrieved cars ---
if st.session_state.search_results:
    st.subheader("Retrieved Cars")
    for result in st.session_state.search_results:
        metadata = result["metadata"]
        st.write(f"- {metadata.get('title')} ({metadata.get('year')}) - {metadata.get('price_num')} € in {metadata.get('city')} - {metadata.get('mileage_km')} km")
