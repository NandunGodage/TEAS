import streamlit as st
import requests
from audio_recorder_streamlit import audio_recorder

API_BASE = "http://localhost:8000"

def render_main_page():
    st.title("🏠 Main Page")
    if st.button("Go to Pronunciation Checker"):
        st.session_state.page = "pronounce"
        st.rerun()

def render_pronounce_checker_page():
    st.title("🎬 Pronunciation Checker")

    # 1) select difficulty
    options = ["எளிதான சொல்", "மிதமான சொல்", "கடினமான சொல்"]
    difficulty = st.radio("Choose difficulty", options, key="pronounce_difficulty")

    # 2) Fetch words
    if st.button("Create Words", key="create_words"):
        payload = {
            "user": 290,
            "text": {"difficulty": difficulty}
        }
        with st.spinner("Fetching words…"):
            resp = requests.post(f"{API_BASE}/generate/words/tamil", json=payload)
        if resp.status_code == 200:
            data = resp.json()
            words = data["result"]["words"]["tamil_words"]
            st.session_state.words = words
            st.session_state.word_index = 0
            st.session_state.transcript = ""
            st.session_state.matched = None
        else:
            st.error(f"Error fetching words: {resp.status_code} {resp.text}")

    # 3) If words exist, show current
    if "words" in st.session_state and st.session_state.words:
        idx = st.session_state.word_index
        word = st.session_state.words[idx]
        st.subheader(f"Word {idx+1}/{len(st.session_state.words)}: {word}")

        # 4) Audio Recorder
        st.markdown("**Record your pronunciation here:**")
        audio_bytes = audio_recorder(
            text="🎤 Record Audio",
            recording_color="#e8b62c",
            neutral_color="#6aa36f",
            icon_size="2x"
        )

        # 5) Submit button
        submit_key = f"submit_audio_{idx}"
        if audio_bytes is not None:
            st.audio(audio_bytes, format="audio/wav")
            if st.button("Submit Pronunciation", key=submit_key):
                # 6) Send to transcription API
                files = {
                    "user": (None, str(290)),
                    "file": ("recorded_audio.wav", audio_bytes, "audio/wav")
                }
                with st.spinner("Transcribing…"):
                    resp = requests.post(
                        f"{API_BASE}/detect/transcription/audio",
                        headers={"Accept": "application/json"},
                        files=files
                    )
                if resp.status_code == 200:
                    st.session_state.transcript = resp.json()["result"].strip()
                else:
                    st.error(f"Transcription error: {resp.status_code} {resp.text}")

                # 7) Match API
                if st.session_state.transcript:
                    match_payload = {
                        "user": 290,
                        "text": {
                            "original": word,
                            "transcript": st.session_state.transcript
                        }
                    }
                    with st.spinner("Checking match…"):
                        mresp = requests.post(f"{API_BASE}/generate/questions/match", json=match_payload)
                    if mresp.status_code == 200:
                        st.session_state.matched = mresp.json()["result"]["matched"]
                    else:
                        st.error(f"Match API error: {mresp.status_code} {mresp.text}")

        # 8) Show transcript & result
        if st.session_state.get("transcript"):
            st.markdown("**Your transcript:**")
            st.write(st.session_state.transcript)

        if st.session_state.get("matched") is True:
            st.success("✅ Correct!")
        elif st.session_state.get("matched") is False:
            st.error("❌ Wrong, try again.")

        # 9) Next word
        if st.session_state.get("matched") is not None and st.button("Next Word", key="next_word"):
            if idx + 1 < len(st.session_state.words):
                st.session_state.word_index += 1
                st.session_state.transcript = ""
                st.session_state.matched = None
                st.rerun()
            else:
                st.success("🎉 You've gone through all the words!")

    # 10) Back to main page
    if st.button("← Back to Main Page"):
        st.session_state.page = "main"
        st.rerun()

def main():
    if "page" not in st.session_state:
        st.session_state.page = "main"

    if st.session_state.page == "main":
        render_main_page()
    elif st.session_state.page == "pronounce":
        render_pronounce_checker_page()

if __name__ == "__main__":
    main()