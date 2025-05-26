
# import streamlit as st
# import requests

# def render_video_extractor_page():
#     st.title("🎬 Video Transcript Extractor")

#     # 1. Upload video
#     uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "mov", "avi"])
#     if uploaded_file:
#         st.video(uploaded_file)

#     # 2. Summarize button
#     if uploaded_file and st.button("Summarize"):
#         with st.spinner("Transcribing video..."):
#             # Send video to /detect/transcription/video
#             files = {
#                 "file": (uploaded_file.name, uploaded_file, uploaded_file.type),
#             }
#             data = {
#                 "user": "your_username",  # Replace with actual username or get from session
#             }
#             try:
#                 response = requests.post(
#                     "http://localhost:8000/detect/transcription/video",
#                     files=files,
#                     data=data,
#                     timeout=120
#                 )
#                 response.raise_for_status()
#                 result_json = response.json()
#             except Exception as e:
#                 st.error(f"Transcription failed: {e}")
#                 return

#             transcript = result_json.get("result")
#             if not transcript:
#                 st.error("No transcript found in response.")
#                 return

#         st.success("Transcription complete!")
#         st.text_area("Transcript", transcript, height=100)

#         with st.spinner("Summarizing transcript..."):
#             # Send transcript to /generate/transcriptions/summary
#             summary_payload = {
#                 "user": 290,  # Replace with actual user id if needed
#                 "text": {"transcript": transcript}
#             }
#             try:
#                 summary_response = requests.post(
#                     "http://localhost:8000/generate/transcriptions/summary",
#                     json=summary_payload,
#                     timeout=60
#                 )
#                 summary_response.raise_for_status()
#                 summary_json = summary_response.json()
#             except Exception as e:
#                 st.error(f"Summary generation failed: {e}")
#                 return

#             result = summary_json.get("result", {})
#             st.markdown("**Tamil Summary:**")
#             st.write(result.get("tamil_summary", "No Tamil summary found."))
#             st.markdown("**English Summary:**")
#             st.write(result.get("english_summary", "No English summary found."))

#     if st.button("Back to Main Page", key="back_to_main_from_video"):
#         st.session_state.page = "main"


import streamlit as st
import requests
import base64
import io
import streamlit.components.v1 as components

# --- Initialize page state ---
if "page" not in st.session_state:
    st.session_state.page = "main"

def show_main():
    st.title("🏠 Main Page")
    st.write("Click below to go to the Video Transcript Extractor.")
    if st.button("Go to Video Extractor"):
        st.session_state.page = "video"

def render_video_extractor_page():
    st.title("🎬 Video Transcript Extractor")

    # 1. Upload video
    uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "mov", "avi"])
    
    # 2. Choose display size
    width = st.number_input("Video width (px)", min_value=100, max_value=1920, value=400, step=50)
    height = st.number_input("Video height (px)", min_value=100, max_value=1080, value=300, step=50)

    if uploaded_file:
        # Read file once
        video_bytes = uploaded_file.read()

        # Encode to base64 for inline HTML
        encoded = base64.b64encode(video_bytes).decode('utf-8')
        video_html = (
            f'<video controls width="{width}" height="{height}">'
            f'  <source src="data:video/mp4;base64,{encoded}" type="{uploaded_file.type}">'
            '  Your browser does not support the video tag.'
            '</video>'
        )
        # Render the HTML video tag
        components.html(video_html, height=height + 35)

    # 3. Summarize button
    if uploaded_file and st.button("Summarize"):
        with st.spinner("Transcribing video..."):
            files = {
                "file": (uploaded_file.name, io.BytesIO(video_bytes), uploaded_file.type),
            }
            data = {"user": 120}  # replace as needed
            try:
                resp = requests.post(
                    "http://localhost:8000/detect/transcription/video",
                    files=files,
                    data=data,
                    timeout=240
                )
                resp.raise_for_status()
                result_json = resp.json()
            except Exception as e:
                st.error(f"Transcription failed: {e}")
                return

            transcript = result_json.get("result")
            if not transcript:
                st.error("No transcript found in response.")
                return

        st.success("Transcription complete!")
        st.text_area("Transcript", transcript, height=150)

        with st.spinner("Summarizing transcript..."):
            payload = {
                "user": 290,  # replace as needed
                "text": {"transcript": transcript}
            }
            try:
                summary_resp = requests.post(
                    "http://localhost:8000/generate/transcriptions/summary",
                    json=payload,
                    timeout=240
                )
                summary_resp.raise_for_status()
                summary_json = summary_resp.json()
            except Exception as e:
                st.error(f"Summary generation failed: {e}")
                return

            result = summary_json.get("result", {})
            st.markdown("**Tamil Summary:**")
            st.write(result.get("tamil_summary", "No Tamil summary found."))
            st.markdown("**English Summary:**")
            st.write(result.get("english_summary", "No English summary found."))

    # Back button
    if st.button("Back to Main Page"):
        st.session_state.page = "main"

# --- Page routing ---
if st.session_state.page == "main":
    show_main()
elif st.session_state.page == "video":
    render_video_extractor_page()