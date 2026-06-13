# Mind Companion - Streamlit Version

A single-file Streamlit app for a mental health companion chatbot for students.

## Setup

1. Install dependencies:
   ```
   pip install streamlit google-generativeai
   ```

2. Get a free Google Gemini API key: https://aistudio.google.com/app/apikey

3. Set the key as an environment variable:
   ```
   # Windows (cmd)
   set GOOGLE_API_KEY=your_key_here

   # PowerShell
   $env:GOOGLE_API_KEY="your_key_here"

   # Mac/Linux
   export GOOGLE_API_KEY=your_key_here
   ```
   OR edit `app.py` and paste your key directly into:
   ```python
   GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "PASTE_YOUR_GOOGLE_API_KEY_HERE")
   ```

4. Run the app:
   ```
   streamlit run app.py
   ```

5. It will open automatically in your browser (usually http://localhost:8501).

## Features / Buttons
- Chat input box - sends message, detects mood, gets empathetic Gemini reply + relaxation tip
- 🌬️ Start/Stop Breathing Exercise - guided 4-3-4 timed breathing animation
- ✨ Get a Quote - random motivational quote
- 🌿 Get a Relaxation Tip - tip based on your last detected mood
- 🆘 Show Support Resources - crisis support message

All input/output text is styled in black on white backgrounds for readability.
