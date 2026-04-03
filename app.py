import streamlit as st
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.title("Bruce - Your Personal AI Advisor")

# -------------------------
# SESSION STATE
# -------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "step" not in st.session_state:
    st.session_state.step = 0

if "user_profile" not in st.session_state:
    st.session_state.user_profile = {}

# -------------------------
# QUESTIONS (10 TOTAL)
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
# SHOW CHAT HISTORY
# -------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# -------------------------
# USER INPUT
# -------------------------
user_input = st.chat_input("Type your response...")

# -------------------------
# ONBOARDING FLOW
# -------------------------
if st.session_state.step < len(questions):

    # First message (greeting)
    if len(st.session_state.messages) == 0:
        first_q = questions[0]
        st.session_state.messages.append({"role": "assistant", "content": first_q})
        with st.chat_message("assistant"):
            st.write(first_q)

    if user_input:
        # Save user input
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.write(user_input)

        # Store structured profile
        keys = [
            "name", "profession", "gender", "dob", "personality",
            "thinking_about", "interests", "frustrations",
            "proud_moment", "future_goal"
        ]

        st.session_state.user_profile[keys[st.session_state.step]] = user_input

        st.session_state.step += 1

        # Ask next question
        if st.session_state.step < len(questions):
            next_q = questions[st.session_state.step]
            st.session_state.messages.append({"role": "assistant", "content": next_q})
            with st.chat_message("assistant"):
                st.write(next_q)
        else:
            completion_msg = f"""
Got it, {st.session_state.user_profile.get("name", "")}.

I now understand you much better.

You can now ask me anything — I’ll keep my answers short, clear, and personalized for you.
"""
            st.session_state.messages.append({"role": "assistant", "content": completion_msg})
            with st.chat_message("assistant"):
                st.write(completion_msg)

# -------------------------
# ADVISOR MODE
# -------------------------
else:
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.write(user_input)

        system_prompt = {
            "role": "system",
            "content": f"""
You are Bruce, a Personal AI Advisor.

User profile:
{st.session_state.user_profile}

Rules:
- Give short, crisp, clear answers (max 3-4 lines)
- Be highly personalized based on user profile
- Identify patterns when possible
- Avoid generic advice
- Ask 1 follow-up question if helpful
"""
        }

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[system_prompt] + st.session_state.messages
        )

        reply = response.choices[0].message.content

        st.session_state.messages.append({"role": "assistant", "content": reply})

        with st.chat_message("assistant"):
            st.write(reply)