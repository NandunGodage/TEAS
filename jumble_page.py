import streamlit as st
import requests
import time
import yaml
from pathlib import Path
from functions_gpt import text_to_audio, play_audio_file

# -------------------------------------------------------------------
# Load your API and TTS configuration
# -------------------------------------------------------------------
with open('./config/config.yml', 'r') as f:
    config = yaml.safe_load(f)

GPT_AUDIO_MODEL = config['GPT_AUDIO_MODEL']
GPT_VOICE       = config['GPT_VOICE']
AUDIO_FILE      = Path("./audio/speech.mp3")

# -------------------------------------------------------------------
# Fetch jumbled sentences from your "generate" endpoint
# -------------------------------------------------------------------
def get_api_response(user_id, difficulty, category):
    url = "http://localhost:8000/generate/questions/jumble"
    payload = {
        "user": user_id,
        "text": {
            "content_topic": category,
            "difficulty": difficulty
        }
    }
    resp = requests.post(url, json=payload)
    if resp.status_code != 200:
        st.error(f"Generate API failed ({resp.status_code}):\n{resp.text}")
        return []

    data         = resp.json().get("result", {})
    difficulties = data.get("difficulty", [])
    return [ item.get("words", []) for item in difficulties ]

# -------------------------------------------------------------------
# Check the user’s arranged sentence
# -------------------------------------------------------------------
def check_api_response(user_id, jumbled, transcript):
    url = "http://localhost:8000/check/questions/jumble"
    payload = {
        "user": user_id,
        "text": {
            "jumbled":    jumbled,
            "transcript": transcript
        }
    }
    resp = requests.post(url, json=payload)
    if resp.status_code == 422:
        st.error("422 Validation error:\n" + resp.text)
        return None
    if resp.status_code != 200:
        st.error(f"Check API failed ({resp.status_code}):\n{resp.text}")
        return None
    return resp.json().get("result", {})

# -------------------------------------------------------------------
# The main Streamlit rendering function
# -------------------------------------------------------------------
def render_jumble_page():
    st.title("ஒரு வாக்கியத்தை உருவாக்க வார்த்தைகளை ஒழுங்குபடுத்துங்கள்")

    # 1) Select difficulty & topic
    difficulty = st.selectbox(
        "கடினத்தன்மைக்கு ஒரு விருப்பத்தைத் தேர்ந்தெடுக்கவும்:",
        ["எளிதான வாக்கியங்கள்", "மிதமான வாக்கியங்கள்", "கடினமான வாக்கியங்கள்"]
    )
    category = st.text_input("வகையை உள்ளிடவும்:")

    # 2) Init session state
    if 'sentences'     not in st.session_state: st.session_state.sentences    = []
    if 'current_idx'   not in st.session_state: st.session_state.current_idx  = 0
    if 'attempts'      not in st.session_state: st.session_state.attempts     = 0
    if 'show_next'     not in st.session_state: st.session_state.show_next    = False
    if 'is_checking'   not in st.session_state: st.session_state.is_checking  = False

    # 3) Generate new set
    if st.button("உருவாக்கு", disabled=(not category.strip())):
        with st.spinner("Generating…"):
            time.sleep(0.3)
            st.session_state.sentences    = get_api_response(
                user_id=290,
                difficulty=difficulty,
                category=category
            )
        # reset all counters/flags
        st.session_state.current_idx  = 0
        st.session_state.attempts     = 0
        st.session_state.show_next    = False
        st.session_state.is_checking  = False

    # 4) If we have sentences, render the current one
    if st.session_state.sentences:
        words = st.session_state.sentences[st.session_state.current_idx]

        st.write("சரியாக ஒழுங்குபடுத்த வேண்டிய வார்த்தைகள்:")
        arranged = st.multiselect(
            "இவைகளை இழுத்து வரிசைப்படுத்தவும் (order matters):",
            options=words,
            default=[]
        )
        transcript = " ".join(arranged)

        col1, col2 = st.columns([3, 1])
        with col2:
            # a) If we've already gotten it right or exhausted tries, show Next
            if st.session_state.show_next:
                if st.button("அடுத்தது"):
                    st.session_state.current_idx = (
                        st.session_state.current_idx + 1
                    ) % len(st.session_state.sentences)
                    st.session_state.attempts    = 0
                    st.session_state.show_next   = False
            else:
                # b) Otherwise show the Check button
                check_disabled = st.session_state.is_checking
                if st.button("சரிபார்க்கவும்", disabled=check_disabled):
                    # mark "in flight" and rerun
                    st.session_state.is_checking = True

                # only if is_checking do we actually call the API
                if st.session_state.is_checking:
                    with st.spinner("Checking…"):
                        result = check_api_response(
                            user_id=290,
                            jumbled=words,
                            transcript=transcript
                        )

                    # immediately re-enable the button
                    st.session_state.is_checking = False

                    # if API failed, bail
                    if not result:
                        return

                    # success?
                    if result.get("isValid"):
                        st.success("👏 மிகச் சரி! வாழ்த்துகள்!")
                        st.session_state.show_next = True

                    else:
                        st.session_state.attempts += 1
                        possible = result.get("possible_answers", [])

                        # third failure → reveal & TTS → allow Next
                        if st.session_state.attempts >= 3:
                            correct = possible[0] if possible else ""
                            text_to_audio(
                                GPT_AUDIO_MODEL,
                                GPT_VOICE,
                                correct,
                                AUDIO_FILE
                            )
                            play_audio_file(AUDIO_FILE)
                            st.warning(
                                "மூன்று முயற்சிகள் முடிந்தன.\n"
                                f"சரியான வாக்கியம்:\n{correct}\n\n"
                            )
                            st.session_state.show_next = True

                        # first or second failure → hint
                        else:
                            st.warning(
                                "தவறு!\n"
                                # + "\n".join(possible)
                                + "\nமீண்டும் முயற்சியிடவும்."
                            )

    # 5) Back button
    if st.button("Back to Main Page"):
        st.session_state.page = "main"

# -------------------------------------------------------------------
# Streamlit entrypoint
# -------------------------------------------------------------------
if __name__ == "__main__":
    if 'page' not in st.session_state:
        st.session_state.page = "new"

    if st.session_state.page == "new":
        render_jumble_page()
    else:
        st.write("Main Page")