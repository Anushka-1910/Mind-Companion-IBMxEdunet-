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
# Mood data
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
    "stressed": ["Try 4-7-8 breathing.", "Break tasks into small steps.", "Take a 10-minute walk."],
    "anxious": ["Try the 5-4-3-2-1 grounding method.", "Write your worries down.", "Relax your shoulders and breathe slowly."],
    "sad": ["Talk to someone you trust.", "Listen to comforting music.", "Write 3 small things you are grateful for."],
    "angry": ["Step away for a few minutes.", "Take slow deep breaths.", "Stretch or walk for 5 minutes."],
    "happy": ["Save this good moment.", "Share kindness with someone.", "Use this energy for one small task."],
    "tired": ["Drink water.", "Rest your eyes.", "Take a short break."],
    "neutral": ["Check in with yourself.", "Take a mindfulness break.", "Pause and breathe."],
}

MOTIVATIONAL_QUOTES = [
    "You are capable of more than you know.",
    "Progress, not perfection.",
    "One small step is still progress.",
    "Be gentle with yourself.",
    "You have survived hard days before."
]

CRISIS_MESSAGE = (
    "If you are having thoughts of harming yourself or feel unsafe, please contact a trusted adult, "
    "college counselor, or emergency support immediately."
)

MOOD_OPTIONS = {
    "Low Energy": "😰",
    "Calm": "🙂",
    "Content": "😊",
    "Cheerful": "😍",
    "Tired": "😴",
    "Anxious": "🥺",
}

# ---------------------------------------------------------------
# Functions
# ---------------------------------------------------------------
def detect_mood(text: str) -> str:
    text_lower = text.lower()
    scores = {mood: 0 for mood in MOOD_KEYWORDS}

    for mood, keywords in MOOD_KEYWORDS.items():
        for kw in keywords:
            if re.search(r"\b" + re.escape(kw) + r"\b", text_lower):
                scores[mood] += 1

    best_mood = max(scores, key=scores.get)
    return "neutral" if scores[best_mood] == 0 else best_mood


def build_prompt(user_message: str, mood: str) -> str:
    return (
        "You are a warm, empathetic mental health companion chatbot for students. "
        "You are not a licensed therapist. Keep the reply short, kind, and helpful.\n\n"
        f"Detected mood: {mood}\n"
        f"Student message: {user_message}\n\n"
        "Respond with empathy and motivation."
    )


def get_bot_reply(user_message: str, mood: str) -> str:
    try:
        response = model.generate_content(build_prompt(user_message, mood))
        return response.text.strip()
    except Exception:
        return "I'm here for you. The AI reply is unavailable right now, so please check your Gemini API key setup."


# ---------------------------------------------------------------
# Page config
# ---------------------------------------------------------------
st.set_page_config(page_title="Mind Companion", page_icon="🌱", layout="wide")

# ---------------------------------------------------------------
# CSS
# ---------------------------------------------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #f7f2ee 0%, #fff7ec 45%, #eef6ff 100%);
}

.block-container {
    padding-top: 1.5rem;
    color: #111111;
}

h1, h2, h3 {
    color: #202020 !important;
}

.phone-card {
    background: white;
    border-radius: 35px;
    padding: 24px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.10);
    min-height: 650px;
}

.hero-card {
    background: #fffaf4;
    border-radius: 24px;
    padding: 22px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.06);
}

.mood-card {
    border-radius: 20px;
    padding: 16px;
    text-align: center;
    color: #111;
    font-weight: 700;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    margin-bottom: 10px;
}

.orange {background:#ff7043;}
.blue {background:#7ea0e8;}
.yellow {background:#ffc928;}
.green {background:#6ed4a5;}

.journey-bar {
    height: 150px;
    border-radius: 30px;
    display: flex;
    align-items: end;
    justify-content: center;
    font-size: 28px;
    padding-bottom: 8px;
}

.session-card {
    background:#ffc400;
    border-radius:28px;
    padding:22px;
    color:#1a1a1a;
    margin-top:15px;
}

.tip-box, .quote-box, .crisis-box, .game-box {
    background:white;
    color:black;
    border-radius:16px;
    padding:14px;
    margin-top:10px;
    box-shadow:0 3px 10px rgba(0,0,0,0.07);
}

.tip-box {border-left:5px solid #81c784;}
.quote-box {border-left:5px solid #64b5f6;}
.crisis-box {border-left:5px solid #e57373; background:#fff5f5;}
.game-box {border-left:5px solid #ba68c8;}

.stButton button {
    background:white;
    color:#222;
    border-radius:14px;
    border:1px solid #eaded6;
    font-weight:700;
}

.stButton button:hover {
    background:#fff0e7;
    border-color:#ff7043;
    color:#ff5722;
}

.stChatMessage {
    background:white !important;
    color:black !important;
    border-radius:16px;
    box-shadow:0 2px 8px rgba(0,0,0,0.06);
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------
# Session state
# ---------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi 👋 I'm your Mind Companion. How are you feeling today?"}
    ]

if "current_mood" not in st.session_state:
    st.session_state.current_mood = "neutral"

if "selected_mood" not in st.session_state:
    st.session_state.selected_mood = "Calm"

if "game_score" not in st.session_state:
    st.session_state.game_score = 0

if "show_quote" not in st.session_state:
    st.session_state.show_quote = False

if "show_tip" not in st.session_state:
    st.session_state.show_tip = False

if "show_crisis" not in st.session_state:
    st.session_state.show_crisis = False

# ---------------------------------------------------------------
# Header
# ---------------------------------------------------------------
st.title("Mind Companion 🌱")
st.write("A calming chatbot with mood tracking, relaxation tools, and a mini game.")

# ---------------------------------------------------------------
# Main layout
# ---------------------------------------------------------------
left, middle, right = st.columns([1.1, 1.2, 1.1])

# ---------------------------------------------------------------
# LEFT: Home mood dashboard
# ---------------------------------------------------------------
with left:
    st.markdown("<div class='phone-card'>", unsafe_allow_html=True)

    st.markdown("""
    <div class='hero-card'>
        <p style='font-size:15px;margin-bottom:4px;'>Welcome back</p>
        <h3 style='margin-top:0;'>Hi, Student 🥺</h3>
        <h2>What's on your mind right now?</h2>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Daily Mood Log")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("😰 Low Energy", use_container_width=True):
            st.session_state.selected_mood = "Low Energy"
            st.session_state.current_mood = "tired"
        st.markdown("<div class='mood-card orange'>😰<br>Low Energy</div>", unsafe_allow_html=True)

        if st.button("😊 Content", use_container_width=True):
            st.session_state.selected_mood = "Content"
            st.session_state.current_mood = "happy"
        st.markdown("<div class='mood-card yellow'>😊<br>Content</div>", unsafe_allow_html=True)

    with c2:
        if st.button("🙂 Calm", use_container_width=True):
            st.session_state.selected_mood = "Calm"
            st.session_state.current_mood = "neutral"
        st.markdown("<div class='mood-card blue'>🙂<br>Calm</div>", unsafe_allow_html=True)

        if st.button("😍 Cheerful", use_container_width=True):
            st.session_state.selected_mood = "Cheerful"
            st.session_state.current_mood = "happy"
        st.markdown("<div class='mood-card green'>😍<br>Cheerful</div>", unsafe_allow_html=True)

    st.markdown("### Mindful Moments")

    m1, m2 = st.columns(2)
    with m1:
        st.markdown("""
        <div class='mood-card yellow'>
            Recharge<br>& Rest<br><br>😴
        </div>
        """, unsafe_allow_html=True)

    with m2:
        st.markdown("""
        <div class='mood-card blue'>
            Emotional<br>Toolkit<br><br>🧘
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------
# MIDDLE: Mood input + chat
# ---------------------------------------------------------------
with middle:
    st.markdown("<div class='phone-card'>", unsafe_allow_html=True)

    emoji = MOOD_OPTIONS.get(st.session_state.selected_mood, "🙂")

    st.markdown(f"""
    <div style='text-align:center;'>
        <h2>Let's capture your <span style='color:#ff7043;'>mood</span> for today.</h2>
        <div style='font-size:90px;'>{emoji}</div>
        <p>Mood Indicator</p>
        <h3>I'm Feeling {st.session_state.selected_mood}</h3>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Save My Feeling", use_container_width=True):
        st.success(f"Your mood '{st.session_state.selected_mood}' is saved 🌿")

    st.markdown("---")
    st.subheader("💬 Chat")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Type how you're feeling...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        mood = detect_mood(user_input)
        st.session_state.current_mood = mood

        reply = get_bot_reply(user_input, mood)

        st.session_state.messages.append({"role": "assistant", "content": reply})

        tip = RELAXATION_TIPS.get(mood, RELAXATION_TIPS["neutral"])[0]
        st.session_state.messages.append({"role": "assistant", "content": f"💡 Tip: {tip}"})

        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------
# RIGHT: Mood journey + tools
# ---------------------------------------------------------------
with right:
    st.markdown("<div class='phone-card'>", unsafe_allow_html=True)

    st.markdown("### Mood Journey")

    days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    emojis = ["😟", "😣", "😍", "😡", "🥺", "😲", "🙄"]
    heights = [110, 85, 130, 95, 150, 120, 90]
    colors = ["#b8f0cf", "#ff7043", "#ffe7a6", "#ff5b3d", "#7299e8", "#a58bea", "#ffc400"]

    cols = st.columns(7)
    for i in range(7):
        with cols[i]:
            st.markdown(
                f"<div class='journey-bar' style='height:{heights[i]}px;background:{colors[i]};'>{emojis[i]}</div>",
                unsafe_allow_html=True,
            )
            st.caption(days[i])

    st.markdown("""
    <div class='session-card'>
        <h4>Next</h4>
        <h1>Session</h1>
        <p>20 July 2025<br>3:00 PM</p>
        <div style='font-size:55px;'>👀</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🧰 Quick Tools")

    if st.button("🌬️ Start Breathing Exercise", use_container_width=True):
        placeholder = st.empty()
        phases = [("Breathe In", 4), ("Hold", 3), ("Breathe Out", 4)]

        for phase, duration in phases:
            for sec in range(duration, 0, -1):
                placeholder.markdown(
                    f"<h2 style='text-align:center;'>{phase}... {sec}</h2>",
                    unsafe_allow_html=True,
                )
                time.sleep(1)

        placeholder.success("Great job 🌿")

    if st.button("✨ Get a Quote", use_container_width=True):
        st.session_state.show_quote = True
        st.session_state.last_quote = random.choice(MOTIVATIONAL_QUOTES)

    if st.session_state.show_quote:
        st.markdown(
            f"<div class='quote-box'>✨ {st.session_state.last_quote}</div>",
            unsafe_allow_html=True,
        )

    if st.button("🌿 Get Relaxation Tip", use_container_width=True):
        mood = st.session_state.current_mood or "neutral"
        st.session_state.last_tip = random.choice(RELAXATION_TIPS.get(mood, RELAXATION_TIPS["neutral"]))
        st.session_state.show_tip = True

    if st.session_state.show_tip:
        st.markdown(
            f"<div class='tip-box'>🌿 {st.session_state.last_tip}</div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("### Mini Relaxation Game 🎮")
    st.caption("Click calm words. Avoid stressful words.")

    st.markdown(
        f"<div class='game-box'>Score: {st.session_state.game_score}</div>",
        unsafe_allow_html=True,
    )

    words = ["stress", "worry", "panic", "peace", "breathe", "relax", "fear", "smile"]
    random.shuffle(words)

    gcols = st.columns(2)
    for i, word in enumerate(words):
        with gcols[i % 2]:
            if st.button(word, key=f"game_{i}", use_container_width=True):
                if word in ["peace", "breathe", "relax", "smile"]:
                    st.session_state.game_score += 1
                    st.success("Good choice 🌿")
                else:
                    st.warning("Let that thought go 💭")

    if st.button("🔄 Reset Game", use_container_width=True):
        st.session_state.game_score = 0
        st.rerun()

    st.markdown("---")

    if st.button("🆘 Show Support Resources", use_container_width=True):
        st.session_state.show_crisis = True

    if st.session_state.show_crisis:
        st.markdown(
            f"<div class='crisis-box'>{CRISIS_MESSAGE}</div>",
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------
# Footer
# ---------------------------------------------------------------
st.markdown("---")
st.caption(
    "⚠️ This chatbot is not a substitute for professional help. "
    "If you are in crisis, please contact a counselor, trusted adult, or emergency services."
)
