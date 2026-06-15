import os
import re
import random
import time
import streamlit as st
import google.generativeai as genai

# ---------------------------------------------------------------
# Google Gemini setup
# ---------------------------------------------------------------
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")

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
        "Ground yourself with the 5-4-3-2-1 technique.",
        "Try progressive muscle relaxation slowly.",
        "Write down your worries on paper.",
    ],
    "sad": [
        "Reach out to a friend or family member.",
        "Listen to uplifting music.",
        "Write three small things you're grateful for today.",
    ],
    "angry": [
        "Step away from the situation for a few minutes.",
        "Try slow deep breathing.",
        "Do stretching or a short walk.",
    ],
    "happy": [
        "Keep a note of what made today good.",
        "Share your positive energy with someone.",
        "Use this mood to complete one task.",
    ],
    "tired": [
        "Drink water and take short breaks.",
        "Try a 15-20 minute power nap.",
        "Step away from screens for a few minutes.",
    ],
    "neutral": [
        "Take a moment to check in with yourself.",
        "A short mindfulness break can help.",
        "Remember to take regular breaks.",
    ],
}

MOTIVATIONAL_QUOTES = [
    "You are capable of more than you know. One step at a time.",
    "It's okay to not be okay sometimes - what matters is that you keep going.",
    "Progress, not perfection. Every small effort counts.",
    "You've survived 100% of your hardest days so far. You've got this.",
    "Be gentle with yourself. You're doing the best you can.",
]

CRISIS_MESSAGE = (
    "I'm really glad you reached out. If you're having thoughts of harming yourself or are in crisis, "
    "please talk to a trusted adult, counselor, or contact emergency support immediately."
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
        "You are NOT a licensed therapist. Give kind, short, practical support.\n\n"
        f"The student's detected mood is: {mood}.\n"
        f"The student says: {user_message}\n\n"
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
            "AI response unavailable right now. Please check your Google API key setup."
        )

# ---------------------------------------------------------------
# Page config
# ---------------------------------------------------------------
st.set_page_config(page_title="Mind Companion", page_icon="🌱", layout="wide")

# ---------------------------------------------------------------
# Styling
# ---------------------------------------------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #eef6f9 0%, #f3f8f0 50%, #fdf6f0 100%);
}

.stTextInput input, textarea, input[type="text"] {
    color: #000000 !important;
    background-color: #ffffff !important;
    border-radius: 10px !important;
}

.stChatMessage {
    color: #000000 !important;
    background-color: #ffffff !important;
    border-radius: 14px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    padding: 6px 10px;
}

.block-container {
    color: #000000;
    padding-top: 1.5rem;
}

h1, h2, h3 {
    color: #2f3e46 !important;
}

.hero-text-card {
    background-color: rgba(255,255,255,0.85);
    border-radius: 14px;
    padding: 16px 20px;
    margin-bottom: 20px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
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

.tip-box, .quote-box, .crisis-box, .game-box {
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

.game-box {
    border-left: 4px solid #ba68c8;
}

.stButton button {
    background-color: #ffffff;
    color: #2f3e46;
    border: 1px solid #d0e0d8;
    border-radius: 10px;
    font-weight: 600;
}

.stButton button:hover {
    background-color: #e8f5e9;
    border-color: #81c784;
    color: #1b5e20;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------
# Header
# ---------------------------------------------------------------
st.title("Mind Companion 🌱")
st.write("Your safe space to talk, breathe, play, and feel better.")

st.markdown(
    "<div class='hero-text-card'><h3>You are not alone.</h3>"
    "<p>Talk to me about stress, exams, friendships, or anything on your mind.</p></div>",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------
# Session state
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

# Game session state
if "game_score" not in st.session_state:
    st.session_state.game_score = 0

# ---------------------------------------------------------------
# Layout
# ---------------------------------------------------------------
chat_col, side_col = st.columns([2, 1])

# ---------------------------------------------------------------
# Chat section
# ---------------------------------------------------------------
with chat_col:
    st.subheader("💬 Chat")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(
                f"<span style='color:#000000'>{msg['content']}</span>",
                unsafe_allow_html=True
            )

    st.markdown(
        f"<div class='mood-badge'>Detected mood: {st.session_state.current_mood}</div>",
        unsafe_allow_html=True,
    )

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

# ---------------------------------------------------------------
# Sidebar tools
# ---------------------------------------------------------------
with side_col:
    st.subheader("🧰 Quick Tools")

    # Breathing Exercise
    st.markdown("**Breathing Exercise**")
    st.caption("Take a guided pause to calm your mind.")

    if st.button("🌬️ Start Breathing Exercise", use_container_width=True):
        st.session_state.show_breathing = True

    if st.session_state.show_breathing:
        placeholder = st.empty()

        phases = [
            ("Breathe In...", 4),
            ("Hold...", 3),
            ("Breathe Out...", 4),
        ]

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

    st.markdown("---")

    # Motivational Quote
    st.markdown("**Motivational Quote**")
    st.caption("A small boost of encouragement.")

    if st.button("✨ Get a Quote", use_container_width=True):
        st.session_state.show_quote = True
        st.session_state.last_quote = random.choice(MOTIVATIONAL_QUOTES)

    if st.session_state.show_quote:
        st.markdown(
            f"<div class='quote-box'>✨ {st.session_state.last_quote}</div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Relaxation Tip
    st.markdown("**Relaxation Tip**")
    st.caption("Get a tip based on your current mood.")

    if st.button("🌿 Get a Relaxation Tip", use_container_width=True):
        mood = st.session_state.current_mood or "neutral"
        tips = RELAXATION_TIPS.get(mood, RELAXATION_TIPS["neutral"])
        st.session_state.last_tip = random.choice(tips)
        st.session_state.show_tip = True

    if st.session_state.show_tip:
        st.markdown(
            f"<div class='tip-box'>🌿 {st.session_state.last_tip}</div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Mini Relaxation Game
    st.markdown("**Mini Relaxation Game 🎮**")
    st.caption("Click the calm words and avoid stressful words.")

    st.markdown(
        f"<div class='game-box'>Score: {st.session_state.game_score}</div>",
        unsafe_allow_html=True,
    )

    words = ["stress", "worry", "panic", "peace", "breathe", "relax", "fear", "smile"]
    random.shuffle(words)

    cols = st.columns(2)

    for i, word in enumerate(words):
        with cols[i % 2]:
            if st.button(word, key=f"word_{i}", use_container_width=True):
                if word in ["peace", "breathe", "relax", "smile"]:
                    st.session_state.game_score += 1
                    st.success("Good choice 🌿")
                else:
                    st.warning("Let that thought go 💭")

    if st.button("🔄 Reset Game", use_container_width=True):
        st.session_state.game_score = 0
        st.rerun()

    st.markdown("---")

    # Crisis Resources
    st.markdown("**Need urgent support?**")
    st.caption("Please reach out if you are struggling.")

    if st.button("🆘 Show Support Resources", use_container_width=True):
        st.session_state.show_crisis = True

    if st.session_state.show_crisis:
        st.markdown(
            f"<div class='crisis-box'>{CRISIS_MESSAGE}</div>",
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------------
# Footer
# ---------------------------------------------------------------
st.markdown("---")
st.caption(
    "⚠️ This chatbot is not a substitute for professional help. "
    "If you are in crisis, please contact a counselor, trusted adult, or emergency services."
)
