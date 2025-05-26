import streamlit as st
import boto3
import yaml
import json
import requests                    # ← new
from botocore.exceptions import NoCredentialsError
from cloud import upload_file_to_s3

with open('./config/config.yml', 'r') as file:
    config_keys = yaml.safe_load(file)

def render_exam_page():
    st.title("Tamil Story Evaluation Exam")
    st.write("Welcome to the Tamil Story Evaluation Exam page!")

    # Image upload section
    st.write("### Upload an Image")
    uploaded_image = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])
    if uploaded_image is not None:
        st.image(uploaded_image, caption="Uploaded Image", use_container_width=True)

        # Align the button to the right
        col1, col2 = st.columns([6, 2])
        with col2:
            evaluate_button = st.button("Evaluate the Story")

        if evaluate_button:
            # 1) upload to S3
            bucket_name = 'homeinspection1'
            public_url = upload_file_to_s3(uploaded_image, bucket_name)
            print(public_url)

            if not public_url:
                st.error("File upload failed.")
                return

            # 2) call your local API instead of generate_reasoning_text
            api_url = "http://localhost:8000/generate/image/evaluation"
            payload = {
                "user": 290,         # ← change this to your real user ID or session var
                "text": public_url
            }
            try:
                response = requests.post(api_url, json=payload, timeout=180)
                response.raise_for_status()
            except requests.RequestException as e:
                st.error(f"Error calling evaluation API: {e}")
                return

            result_json = response.json()
            # server wraps the actual fields under "result"
            exam_result = result_json.get("result", {})

            # Extract fields
            marks = exam_result.get("marks", 0)
            corrected_sentence = exam_result.get("corrected_sentence", "")
            is_mistake = exam_result.get("is_mistake", False)
            comments = exam_result.get("comments", "")

            # Display
            st.error(f"Marks: {marks}")
            st.write("------------------------------------")
            if is_mistake:
                st.warning(corrected_sentence)
            else:
                st.success("Very Good!!!")
            st.write("------------------------------------")
            st.info(comments)

    # Navigation back to main
    if st.button("Back to Main Page"):
        st.session_state.page = "main"