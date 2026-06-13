"""
Mind Companion - Mental Health Chatbot for Students (Streamlit version)
-------------------------------------------------------------------------
Run with:
    pip install streamlit google-generativeai
    streamlit run app.py

Set your Google Gemini API key as an environment variable GOOGLE_API_KEY,
or paste it directly in GOOGLE_API_KEY below.
Get a free key at: https://aistudio.google.com/app/apikey
"""

import os
import re
import random
import time
import streamlit as st
import google.generativeai as genai

# ---------------------------------------------------------------
# Google Gemini setup
# ---------------------------------------------------------------
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "PASTE_YOUR_GOOGLE_API_KEY_HERE")
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# ---------------------------------------------------------------
# Mood detection
# ---------------------------------------------------------------
MOOD_KEYWORDS = {
    "stressed": ["stress", "stressed", "overwhelmed", "pressure", "deadline", "exam", "exams", "workload"],
    "anxious": ["anxious", "anxiety", "nervous", "worried", "panic", "scared", "afraid"],
    "sad": ["sad", "depressed", "down", "lonely", "alone", "hopeless", "cry", "crying", "upset"],
    "angry": ["angry", "frustrated", "annoyed", "mad", "furious", "irritated"],
    "happy": ["happy", "great", "good", "excited", "awesome", "joy", "glad", "wonderful"],
    "tired": ["tired", "exhausted", "sleepy", "fatigue", "burned out", "burnt out"],
}

RELAXATION_TIPS = {
    "stressed": [
        "Try the 4-7-8 breathing technique: inhale for 4 seconds, hold for 7, exhale for 8.",
        "Break your tasks into smaller steps and tackle just one at a time.",
        "Take a 10-minute walk outside to reset your mind.",
    ],
    "anxious": [
        "Ground yourself with the 5-4-3-2-1 technique: name 5 things you see, 4 you feel, 3 you hear, 2 you smell, 1 you taste.",
        "Try progressive muscle relaxation - tense and release each muscle group slowly.",
        "Write down your worries on paper to get them out of your head.",
    ],
    "sad": [
        "Reach out to a friend or family member, even just to say hi.",
        "Listen to your favorite uplifting music or watch something that makes you smile.",
        "Try journaling about three small things you're grateful for today.",
    ],
    "angry": [
        "Step away from the situation for a few minutes before responding.",
        "Try slow deep breathing: in through the nose, out through the mouth.",
        "Channel the energy into a quick physical activity like stretching or a short walk.",
    ],
    "happy": [
        "Great to hear! Keep a note of what made today good - it's nice to look back on.",
        "Share your positive energy with someone else - send a kind message to a friend.",
        "Use this good mood to tackle a task you've been putting off!",
    ],
    "tired": [
        "Make sure you're staying hydrated and taking short breaks every hour.",
        "Try a quick power nap (15-20 minutes) if possible.",
        "Stretch your body and step away from screens for a few minutes.",
    ],
    "neutral": [
        "Take a moment to check in with yourself - how are you really feeling?",
        "A short mindfulness break can help you stay centered through the day.",
        "Remember to take regular breaks between study sessions.",
    ],
}

MOTIVATIONAL_QUOTES = [
    "You are capable of more than you know. One step at a time.",
    "It's okay to not be okay sometimes - what matters is that you keep going.",
    "Progress, not perfection. Every small effort counts.",
    "You've survived 100% of your hardest days so far. You've got this.",
    "Be gentle with yourself. You're doing the best you can with what you have.",
    "Difficult roads often lead to beautiful destinations.",
    "Your feelings are valid, and so is your strength to overcome them.",
]

CRISIS_MESSAGE = (
    "I'm really glad you reached out. If you're having thoughts of harming yourself or are in crisis, "
    "please consider talking to a trusted adult, counselor, or contacting a crisis helpline in your country "
    "right away. You deserve support, and you don't have to go through this alone."
)


def detect_mood(text: str) -> str:
    text_lower = text.lower()
    scores = {mood: 0 for mood in MOOD_KEYWORDS}
    for mood, keywords in MOOD_KEYWORDS.items():
        for kw in keywords:
            if re.search(r"\b" + re.escape(kw) + r"\b", text_lower):
                scores[mood] += 1
    best_mood = max(scores, key=scores.get)
    if scores[best_mood] == 0:
        return "neutral"
    return best_mood


def build_prompt(user_message: str, mood: str) -> str:
    return (
        "You are a warm, empathetic mental health companion chatbot for students. "
        "You are NOT a licensed therapist, and you should gently remind users to seek professional "
        "help for serious issues, but otherwise you should respond with kindness, validation, "
        "encouragement, and practical, gentle suggestions. Keep responses concise (3-5 sentences), "
        "warm, and conversational. Avoid sounding clinical.\n\n"
        f"The student's detected mood is: {mood}.\n"
        f"The student says: \"{user_message}\"\n\n"
        "Respond with empathy and motivation."
    )


def get_bot_reply(user_message: str, mood: str) -> str:
    try:
        prompt = build_prompt(user_message, mood)
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return (
            "Thanks for sharing that with me. I'm here for you. "
            "(Note: AI response unavailable right now - check your Google API key setup.) "
            f"Error: {e}"
        )


# ---------------------------------------------------------------
# Page config & styling
# ---------------------------------------------------------------
st.set_page_config(page_title="Mind Companion", page_icon="🌱", layout="wide")

st.markdown("""
<style>
/* Overall app background - soft gradient */
.stApp {
    background: linear-gradient(135deg, #eef6f9 0%, #f3f8f0 50%, #fdf6f0 100%);
}

/* Make all typed/input text black on white background */
.stTextInput input, .stChatInputContainer textarea, textarea,
input[type="text"] {
    color: #000000 !important;
    background-color: #ffffff !important;
    border-radius: 10px !important;
}

/* Chat input bar */
.stChatInput, .stChatInputContainer {
    background-color: #ffffff !important;
    border-radius: 12px !important;
}

/* Chat message bubbles */
.stChatMessage {
    color: #000000 !important;
    background-color: #ffffff !important;
    border-radius: 14px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    padding: 6px 10px;
}

/* General body text */
.block-container {
    color: #000000;
    padding-top: 1.5rem;
}

/* Headings accent color */
h1, h2, h3 {
    color: #2f3e46 !important;
}

/* Card-like containers for sidebar tools */
.tool-card {
    background-color: #ffffff;
    border-radius: 16px;
    padding: 14px;
    margin-bottom: 18px;
    box-shadow: 0 3px 10px rgba(0,0,0,0.07);
}

.tip-box, .quote-box, .crisis-box {
    background-color: #ffffff;
    color: #000000;
    border-radius: 10px;
    padding: 12px;
    margin-top: 10px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.tip-box {
    border-left: 4px solid #81c784;
}
.quote-box {
    border-left: 4px solid #64b5f6;
}
.crisis-box {
    background-color: #fff5f5;
    border-left: 4px solid #e57373;
}

.mood-badge {
    background-color: #fff8e1;
    color: #5d4037;
    border: 1px solid #ffe082;
    border-radius: 20px;
    padding: 6px 16px;
    display: inline-block;
    margin-top: 8px;
    margin-bottom: 8px;
    font-weight: 600;
}

/* Buttons */
.stButton button {
    background-color: #ffffff;
    color: #2f3e46;
    border: 1px solid #d0e0d8;
    border-radius: 10px;
    font-weight: 600;
    transition: all 0.2s ease;
}
.stButton button:hover {
    background-color: #e8f5e9;
    border-color: #81c784;
    color: #1b5e20;
}

/* Rounded images */
.stImage img {
    border-radius: 14px;
}

/* Hero text card */
.hero-text-card {
    background-color: rgba(255,255,255,0.85);
    border-radius: 14px;
    padding: 16px 20px;
    margin-top: -10px;
    margin-bottom: 20px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------
# Header & hero image
# ---------------------------------------------------------------
col1, col2 = st.columns([1, 4])
with col2:
    st.title("Mind Companion 🌱")
    st.write("Your safe space to talk, breathe, and feel better.")

st.markdown(
    "<div class='hero-text-card'><h3>You are not alone.</h3>"
    "<p>Talk to me about anything that's on your mind - stress, exams, friendships, or just life. "
    "I'm here to listen.</p></div>",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------
# Session state init
# ---------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi there 👋 I'm your Mind Companion. How are you feeling today?"}
    ]
if "current_mood" not in st.session_state:
    st.session_state.current_mood = "neutral"
if "show_breathing" not in st.session_state:
    st.session_state.show_breathing = False
if "show_quote" not in st.session_state:
    st.session_state.show_quote = False
if "show_tip" not in st.session_state:
    st.session_state.show_tip = False
if "show_crisis" not in st.session_state:
    st.session_state.show_crisis = False

# ---------------------------------------------------------------
# Layout: Chat (left) + Sidebar tools (right)
# ---------------------------------------------------------------
chat_col, side_col = st.columns([2, 1])

with chat_col:
    st.subheader("💬 Chat")

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(f"<span style='color:#000000'>{msg['content']}</span>", unsafe_allow_html=True)

    # Mood badge
    if st.session_state.current_mood:
        st.markdown(
            f"<div class='mood-badge'>Detected mood: {st.session_state.current_mood}</div>",
            unsafe_allow_html=True,
        )

    # Chat input
    user_input = st.chat_input("Type how you're feeling...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        mood = detect_mood(user_input)
        st.session_state.current_mood = mood

        with st.spinner("Thinking..."):
            reply = get_bot_reply(user_input, mood)

        st.session_state.messages.append({"role": "assistant", "content": reply})

        tip = RELAXATION_TIPS.get(mood, RELAXATION_TIPS["neutral"])[0]
        st.session_state.messages.append({"role": "assistant", "content": f"💡 Tip: {tip}"})

        st.rerun()

with side_col:
    st.subheader("🧰 Quick Tools")

    # ---------------- Breathing Exercise ----------------
    st.markdown("**Breathing Exercise**")
    st.caption("Take a guided pause to calm your nervous system.")

    if st.button("🌬️ Start Breathing Exercise", use_container_width=True):
        st.session_state.show_breathing = True

    if st.session_state.show_breathing:
        placeholder = st.empty()
        stop = st.button("Stop Breathing Exercise", use_container_width=True)
        if not stop:
            phases = [("Breathe In...", 4), ("Hold...", 3), ("Breathe Out...", 4)]
            for phase_text, duration in phases:
                for remaining in range(duration, 0, -1):
                    placeholder.markdown(
                        f"<div style='text-align:center; font-size:1.4em; color:#000000;'>"
                        f"{phase_text} ({remaining})</div>",
                        unsafe_allow_html=True,
                    )
                    time.sleep(1)
            placeholder.markdown(
                "<div style='text-align:center; font-size:1.4em; color:#000000;'>Great job! 🌿</div>",
                unsafe_allow_html=True,
            )
            st.session_state.show_breathing = False
        else:
            st.session_state.show_breathing = False
            placeholder.empty()

    st.markdown("---")

    # ---------------- Motivational Quote ----------------
    st.markdown("**Motivational Quote**")
    st.caption("A little boost of encouragement.")

    if st.button("✨ Get a Quote", use_container_width=True):
        st.session_state.show_quote = True
        st.session_state.last_quote = random.choice(MOTIVATIONAL_QUOTES)

    if st.session_state.show_quote:
        st.markdown(
            f"<div class='quote-box'>✨ {st.session_state.get('last_quote', '')}</div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ---------------- Relaxation Tip ----------------
    st.markdown("**Relaxation Tip**")
    st.caption("Get a personalized tip based on your current mood.")

    if st.button("🌿 Get a Relaxation Tip", use_container_width=True):
        mood = st.session_state.current_mood or "neutral"
        tips = RELAXATION_TIPS.get(mood, RELAXATION_TIPS["neutral"])
        st.session_state.last_tip = random.choice(tips)
        st.session_state.show_tip = True

    if st.session_state.show_tip:
        st.markdown(
            f"<div class='tip-box'>🌿 {st.session_state.get('last_tip', '')}</div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ---------------- Crisis Resources ----------------
    st.markdown("**Need urgent support?**")
    st.caption("If you're struggling, please reach out for help.")

    if st.button("🆘 Show Support Resources", use_container_width=True):
        st.session_state.show_crisis = True

    if st.session_state.show_crisis:
        st.markdown(f"<div class='crisis-box'>{CRISIS_MESSAGE}</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------
# Footer
# ---------------------------------------------------------------
st.markdown("---")
st.caption(
    "⚠️ This chatbot is not a substitute for professional help. "
    "If you are in crisis, please contact a counselor, trusted adult, or local emergency services."
)
