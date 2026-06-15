import re
import random
import time
import streamlit as st
import google.generativeai as genai

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")

MOOD_KEYWORDS = {
    "stressed": ["stress", "stressed", "overwhelmed", "pressure", "deadline", "exam", "exams"],
    "anxious": ["anxious", "anxiety", "nervous", "worried", "panic", "scared"],
    "sad": ["sad", "depressed", "down", "lonely", "hopeless", "cry"],
    "angry": ["angry", "frustrated", "annoyed", "mad", "irritated"],
    "happy": ["happy", "great", "good", "excited", "joy"],
    "tired": ["tired", "exhausted", "sleepy", "fatigue"],
}

RELAXATION_TIPS = {
    "stressed": ["Try 4-7-8 breathing.", "Break work into small steps.", "Take a short walk."],
    "anxious": ["Try 5-4-3-2-1 grounding.", "Write your worries down.", "Breathe slowly."],
    "sad": ["Talk to someone you trust.", "Listen to comforting music.", "Write 3 good things."],
    "angry": ["Pause before replying.", "Take deep breaths.", "Do light stretching."],
    "happy": ["Save this good moment.", "Share your happiness.", "Complete one small task."],
    "tired": ["Drink water.", "Rest your eyes.", "Take a short break."],
    "neutral": ["Pause and breathe.", "Check in with yourself.", "Take a small break."],
}

QUOTES = [
    "One small step is still progress.",
    "You are doing better than you think.",
    "Be gentle with yourself.",
    "Progress, not perfection.",
]

CRISIS_MESSAGE = (
    "If you feel unsafe or have thoughts of harming yourself, please contact a trusted adult, "
    "college counselor, or emergency support immediately."
)


def detect_mood(text):
    text = text.lower()
    scores = {mood: 0 for mood in MOOD_KEYWORDS}

    for mood, words in MOOD_KEYWORDS.items():
        for word in words:
            if re.search(r"\b" + re.escape(word) + r"\b", text):
                scores[mood] += 1

    best = max(scores, key=scores.get)
    return "neutral" if scores[best] == 0 else best


def get_bot_reply(user_message, mood):
    try:
        prompt = f"""
You are a warm mental health companion for students.
You are not a therapist.
Reply in 3-5 short, kind sentences.

Detected mood: {mood}
Student message: {user_message}
"""
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception:
        return "I'm here for you. The AI reply is unavailable right now, so please check your Gemini API key setup."


st.set_page_config(page_title="Mind Companion", page_icon="🌱", layout="wide")

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #fff7ef 0%, #f5fbff 100%);
}

.block-container {
    padding-top: 1rem;
}

* {
    color: #111111 !important;
}

h1, h2, h3, h4, p, span, div {
    color: #111111 !important;
}

.main-title {
    text-align: center;
    font-size: 48px;
    font-weight: 900;
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    font-size: 18px;
    color: #384152 !important;
    margin-bottom: 30px;
}

.card {
    background: rgba(255,255,255,0.82);
    border-radius: 24px;
    padding: 22px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.08);
    margin-bottom: 18px;
}

.mood-card {
    border-radius: 18px;
    padding: 16px;
    text-align: center;
    font-weight: 700;
    min-height: 100px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

.orange { background: #ff7043; }
.blue { background: #9ec9ff; }
.yellow { background: #ffe082; }
.green { background: #8ee6b8; }
.purple { background: #c6a9ff; }
.pink { background: #ffb3b3; }

.chat-box {
    background: white;
    border-radius: 18px;
    padding: 16px;
    margin-bottom: 14px;
    box-shadow: 0 3px 10px rgba(0,0,0,0.07);
}

.user-box {
    background: #fff0df;
    border-radius: 18px;
    padding: 16px;
    margin-bottom: 14px;
    margin-left: 80px;
    text-align: right;
}

.journey-bar {
    border-radius: 28px;
    text-align: center;
    font-size: 28px;
    padding-top: 70px;
}

.session-card {
    background: #ffc400;
    border-radius: 24px;
    padding: 22px;
    margin-top: 18px;
}

.tool-card {
    background: white;
    border-radius: 18px;
    padding: 16px;
    box-shadow: 0 3px 10px rgba(0,0,0,0.07);
    margin-bottom: 12px;
}

.stButton button {
    background: white !important;
    color: #111111 !important;
    border-radius: 14px !important;
    border: 1px solid #dddddd !important;
    font-weight: 700 !important;
}

.stButton button:hover {
    background: #fff0e7 !important;
    border-color: #ff7043 !important;
}

textarea, input {
    color: #111111 !important;
    background-color: white !important;
}

.stChatInput textarea {
    color: #111111 !important;
    background-color: white !important;
}
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi 👋 I'm your Mind Companion. How are you feeling today?"}
    ]

if "current_mood" not in st.session_state:
    st.session_state.current_mood = "neutral"

if "selected_mood" not in st.session_state:
    st.session_state.selected_mood = "Calm 🙂"

if "game_score" not in st.session_state:
    st.session_state.game_score = 0

st.markdown("<div class='main-title'>🌱 Mind Companion</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='subtitle'>A calming chatbot with mood tracking, relaxation tools, and a mini game.</div>",
    unsafe_allow_html=True
)

left, center, right = st.columns([1, 1.25, 1])

with left:
    st.markdown("""
    <div class='card'>
        <h3>👋 Welcome back</h3>
        <h1>Hi, Student 😊</h1>
        <h3>What’s on <span style='color:#ff5722 !important;'>your mind</span> right now?</h3>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Daily Mood Log")

    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("😰 Low", use_container_width=True):
            st.session_state.selected_mood = "Low Energy 😰"
            st.session_state.current_mood = "tired"
        st.markdown("<div class='mood-card orange'>😰<br>Low Energy</div>", unsafe_allow_html=True)

    with c2:
        if st.button("🙂 Calm", use_container_width=True):
            st.session_state.selected_mood = "Calm 🙂"
            st.session_state.current_mood = "neutral"
        st.markdown("<div class='mood-card blue'>🙂<br>Calm</div>", unsafe_allow_html=True)

    with c3:
        if st.button("😊 Content", use_container_width=True):
            st.session_state.selected_mood = "Content 😊"
            st.session_state.current_mood = "happy"
        st.markdown("<div class='mood-card yellow'>😊<br>Content</div>", unsafe_allow_html=True)

    c4, c5, c6 = st.columns(3)

    with c4:
        if st.button("😍 Cheerful", use_container_width=True):
            st.session_state.selected_mood = "Cheerful 😍"
            st.session_state.current_mood = "happy"
        st.markdown("<div class='mood-card green'>😍<br>Cheerful</div>", unsafe_allow_html=True)

    with c5:
        if st.button("😴 Tired", use_container_width=True):
            st.session_state.selected_mood = "Tired 😴"
            st.session_state.current_mood = "tired"
        st.markdown("<div class='mood-card purple'>😴<br>Tired</div>", unsafe_allow_html=True)

    with c6:
        if st.button("🥺 Anxious", use_container_width=True):
            st.session_state.selected_mood = "Anxious 🥺"
            st.session_state.current_mood = "anxious"
        st.markdown("<div class='mood-card pink'>🥺<br>Anxious</div>", unsafe_allow_html=True)

    st.subheader("Mindful Moments")

    r1, r2 = st.columns(2)

    with r1:
        st.markdown("<div class='mood-card yellow'>Recharge<br>& Rest<br><br>😴</div>", unsafe_allow_html=True)

    with r2:
        st.markdown("<div class='mood-card blue'>Emotional<br>Toolkit<br><br>🧘</div>", unsafe_allow_html=True)

with center:
    st.subheader("💬 Chat")
    st.write("Talk, share, and feel better.")
    st.subheader(f"Today's Mood: {st.session_state.selected_mood}")

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"<div class='user-box'>{msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-box'>🤖 {msg['content']}</div>", unsafe_allow_html=True)

    user_input = st.chat_input("Type your message here...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        mood = detect_mood(user_input)
        st.session_state.current_mood = mood

        reply = get_bot_reply(user_input, mood)
        st.session_state.messages.append({"role": "assistant", "content": reply})

        tip = RELAXATION_TIPS.get(mood, RELAXATION_TIPS["neutral"])[0]
        st.session_state.messages.append({"role": "assistant", "content": f"💡 Tip: {tip}"})

        st.rerun()

with right:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📈 Mood Journey")

    days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    emojis = ["😟", "😣", "😍", "😡", "🥺", "😲", "🙂"]
    heights = [130, 100, 150, 115, 155, 130, 105]
    colors = ["#b8f0cf", "#ff8a3d", "#ffe082", "#ff5b3d", "#7eb6ff", "#c6a9ff", "#ffc400"]

    cols = st.columns(7)

    for i in range(7):
        with cols[i]:
            st.markdown(
                f"<div class='journey-bar' style='height:{heights[i]}px;background:{colors[i]};'>{emojis[i]}</div>",
                unsafe_allow_html=True
            )
            st.caption(days[i])

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class='session-card'>
        <h3>📅 Next Session</h3>
        <h1>Session</h1>
        <p>20 July 2025<br>3:00 PM</p>
        <div style='font-size:50px;'>👀 😴</div>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("🧰 Quick Tools")

    q1, q2 = st.columns(2)

    with q1:
        if st.button("🌬️ Breathing", use_container_width=True):
            placeholder = st.empty()
            phases = [("Breathe In", 4), ("Hold", 3), ("Breathe Out", 4)]

            for phase, duration in phases:
                for sec in range(duration, 0, -1):
                    placeholder.markdown(f"## {phase}... {sec}")
                    time.sleep(1)

            placeholder.success("Great job 🌿")

        if st.button("🌿 Tip", use_container_width=True):
            mood = st.session_state.current_mood
            tip = random.choice(RELAXATION_TIPS.get(mood, RELAXATION_TIPS["neutral"]))
            st.markdown(f"<div class='tool-card'>🌿 {tip}</div>", unsafe_allow_html=True)

    with q2:
        if st.button("✨ Quote", use_container_width=True):
            st.markdown(f"<div class='tool-card'>✨ {random.choice(QUOTES)}</div>", unsafe_allow_html=True)

        if st.button("🎮 Game", use_container_width=True):
            st.info("Play the mini game below!")

    st.subheader("🎮 Mini Game")
    st.markdown(f"<div class='tool-card'>Score: {st.session_state.game_score}</div>", unsafe_allow_html=True)

    words = ["stress", "worry", "panic", "peace", "breathe", "relax", "fear", "smile"]
    random.shuffle(words)

    g1, g2 = st.columns(2)

    for i, word in enumerate(words):
        with [g1, g2][i % 2]:
            if st.button(word, key=f"game_{i}", use_container_width=True):
                if word in ["peace", "breathe", "relax", "smile"]:
                    st.session_state.game_score += 1
                    st.success("Good choice 🌿")
                else:
                    st.warning("Let that thought go 💭")

    if st.button("🔄 Reset Game", use_container_width=True):
        st.session_state.game_score = 0
        st.rerun()

    if st.button("🆘 Support Resources", use_container_width=True):
        st.error(CRISIS_MESSAGE)

st.markdown("---")
st.caption(
    "⚠️ This chatbot is not a substitute for professional help. "
    "If you are in crisis, contact a counselor, trusted adult, or emergency services."
)
