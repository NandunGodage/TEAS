# streamlit_app.py

import streamlit as st
import json
import requests

# Function to render the main page
def main_page():
    st.title("Tamil Story Generator")

    # Input for user story title
    story_title = st.text_input("Enter a Tamil Story Title")

    # Dropdown for version selection
    version = st.selectbox("Select Version", ["Version_01", "Version_02"])

    # Initialize variables for API payload
    slider_value = 0

    # Display slider only if Version_02 is selected
    if version == "Version_02":
        slider_value = st.slider("Select a Grade", min_value=1, max_value=5, step=1)

    # Initialize a placeholder for the button to control its state
    button_placeholder = st.empty()

    # Initialize a variable to control the button state
    button_disabled = False

    # Function to make the API call and display result
    def generate_story():
        nonlocal button_disabled
        button_disabled = True  # Disable button during API call
        if story_title.strip() != "":
            # Show spinner to indicate processing
            with st.spinner("Generating story..."):
                # Prepare API payload
                grade_mapping = {1: 30, 2: 40, 3: 50, 4: 60, 5: 70}
                mapped_slider_value = grade_mapping.get(slider_value, 0)

                inputs = {
                    "user": 290,
                    "text": f"{story_title},{mapped_slider_value}",
                }

                try:
                    response = requests.post(
                        url="http://localhost:8000/generate/story/tamil",
                        data=json.dumps(inputs),
                        headers={"Content-Type": "application/json"}
                    )

                    if response.status_code == 200:
                        response_data = response.json()
                        if "result" in response_data and response_data["result"]:
                            story_heading = response_data["result"].get("heading", "No Heading")
                            story_content = response_data["result"].get("story", "No Story Content")
                            st.subheader(f"Story: {story_heading}")
                            st.write(story_content)
                        else:
                            st.error("Story generation failed. Try again.")
                    else:
                        st.error(f"Request failed with status: {response.status_code}")

                except Exception as e:
                    st.error(f"An error occurred: {e}")
                finally:
                    button_disabled = False  # Re-enable button after API call
        else:
            st.warning("Please enter a story title.")
            button_disabled = False  # Re-enable button if no title is provided

    # Render button with a unique key and control its click behavior
    if button_placeholder.button("Generate Story", disabled=button_disabled, key="main_button"):
        generate_story()

# Initialize session state for navigation
if "page" not in st.session_state:
    st.session_state.page = "main"

# Check the current page and render the appropriate content
if st.session_state.page == "exam":
    from exam_page import render_exam_page
    render_exam_page()
elif st.session_state.page == "jumble_words_game":
    from jumble_page import render_jumble_page
    render_jumble_page()
elif st.session_state.page == "video_extractor":
    from video_extractor_page import render_video_extractor_page
    render_video_extractor_page()
elif st.session_state.page == "pronounce_checker":
    from pronounce_checker_page import render_pronounce_checker_page
    render_pronounce_checker_page()
else:
    main_page()

# Sidebar buttons with unique keys
if st.sidebar.button("Tamil Story Evaluation Exam", key="sidebar_button"):
    st.session_state.page = "exam"

if st.sidebar.button("Jumble Words Game", key="jumble_page_button"):
    st.session_state.page = "jumble_words_game"

if st.sidebar.button("Video Transcript Extractor", key="video_extractor_button"):
    st.session_state.page = "video_extractor"

if st.sidebar.button("Pronouncation Checker", key="pronounce_checker_button"):
    st.session_state.page = "pronounce_checker"


# pronounce_checker_page