import streamlit as st
from groq import Groq
import os
import json
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(page_title="Bruce AI Advisor")

# -------------------------
# USER DATABASE FUNCTIONS
# -------------------------
def load_all_users():
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_all_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f)

def load_user_data(username):
    users = load_all_users()
    return users.get(username, {"profile": {}, "messages": [], "step": 0})

def save_user_data(username, data):
    users = load_all_users()
    users[username] = data
    save_all_users(users)

# -------------------------
# LOGIN / REGISTER SYSTEM
# -------------------------
st.sidebar.title("Login / Register")

users = load_all_users()

username_input = st.sidebar.text_input("Username")
password_input = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Login"):
    if username_input in users and users[username_input]["password"] == password_input:
        st.session_state["user"] = username_input
        st.success("Logged in successfully!")
        st.rerun()
    else:
        st.sidebar.error("Invalid credentials")

# REGISTER
st.sidebar.subheader("New User? Register")
new_user = st.sidebar.text_input("New Username")
new_pass = st.sidebar.text_input("New Password", type="password")

if st.sidebar.button("Register"):
    if new_user and new_pass:
        users = load_all_users()
        if new_user not in users:
            users[new_user] = {
                "password": new_pass,
                "profile": {},
                "messages": [],
                "step": 0
            }
            save_all_users(users)
            st.sidebar.success("User created! Please login.")
        else:
            st.sidebar.error("User already exists")

# CHECK LOGIN
authentication_status = False
if "user" in st.session_state:
    username = st.session_state["user"]
    authentication_status = True

# -------------------------
# MAIN APP
# -------------------------
if authentication_status:

    st.title(f"Bruce - AI Advisor (Welcome {username})")

    user_data = load_user_data(username)

    if "messages" not in st.session_state:
        st.session_state.messages = user_data["messages"]

    if "user_profile" not in st.session_state:
        st.session_state.user_profile = user_data["profile"]

    if "step" not in st.session_state:
        st.session_state.step = user_data.get("step", 0)

    # -------------------------
    # QUESTIONS (FIXED FLOW)
    # -------------------------
    questions = [
        "Hey, I’m Bruce — your personal AI advisor 👋\n\nLet’s start simple.\n\nWhat’s your name?",
        
        "Nice to meet you! What do you do currently?\n(e.g., student, working professional, freelancer, etc.)",
        
        "What’s your gender?",
        
        "What’s your date of birth?",
        
        "How would you describe your personality?\n(e.g., introvert, extrovert, ambivert)",
        
        "What’s something you’ve been thinking a lot about lately?\n(e.g., career, money, relationships, self-growth)",
        
        "What kind of activities or work make you feel excited or interested?\n(e.g., building things, talking to people, analyzing, creativity)",
        
        "What’s something in your life right now that feels frustrating?\n(e.g., lack of clarity, no progress, distractions)",
        
        "Tell me about a time you felt proud or satisfied.\nWhat were you doing?",
        
        "If things go well in the next 1–2 years, what would you want your life to look like?\n(e.g., job, income, lifestyle)"
    ]

    # -------------------------
    # SHOW CHAT
    # -------------------------
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # FIRST QUESTION INIT
    if len(st.session_state.messages) == 0:
        first_q = questions[0]
        st.session_state.messages.append({"role": "assistant", "content": first_q})
        st.rerun()

    user_input = st.chat_input("Type here...")

    # -------------------------
    # ONBOARDING (FIXED)
    # -------------------------
    if st.session_state.step < len(questions):

        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})

            keys = [
                "name", "profession", "gender", "dob", "personality",
                "thinking", "interests", "frustrations",
                "proud", "future"
            ]

            st.session_state.user_profile[keys[st.session_state.step]] = user_input

            st.session_state.step += 1

            if st.session_state.step < len(questions):
                next_q = questions[st.session_state.step]
                st.session_state.messages.append({"role": "assistant", "content": next_q})
            else:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "Got it. I understand you now. Ask me anything."
                })

            st.rerun()

    # -------------------------
    # ADVISOR MODE
    # -------------------------
    else:
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})

            system_prompt = {
                "role": "system",
                "content": f"""
You are Bruce, a personal AI advisor.

User profile:
{st.session_state.user_profile}

Rules:
- Keep answers short (max 3 lines)
- Be specific to user
- Give actionable advice
"""
            }

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[system_prompt] + st.session_state.messages
            )

            reply = response.choices[0].message.content

            st.session_state.messages.append({"role": "assistant", "content": reply})

            st.rerun()

    # -------------------------
    # SAVE USER DATA
    # -------------------------
    save_user_data(username, {
        "password": users[username]["password"],
        "profile": st.session_state.user_profile,
        "messages": st.session_state.messages,
        "step": st.session_state.step
    })

else:
    st.warning("Please login from sidebar")