import streamlit as st
import requests
import base64
from docx import Document
from docx.shared import Inches
from io import BytesIO

#Trial commnet - ignore this 2025

# Constants for better maintainability
API_URL = "http://localhost:8000/gemini-generate"
MAX_IMAGE_SIZE_MB = 10  # Example: Limit image size to prevent issues
DEFAULT_PROMPT_CONTEXT = "None"

# Session state initialization (unchanged)
if "test_cases_result" not in st.session_state:
    st.session_state.test_cases_result = None
if "uploaded_files_info" not in st.session_state:
    st.session_state.uploaded_files_info = None
if "generation_date" not in st.session_state:
    st.session_state.generation_date = None


# Improved function to encode images with validation
def encode_image_to_base64(image_file):
    try:
        # Check file size (improvement: prevent large files from causing issues)
        image_file.seek(0, 2)  # Seek to end to get size
        if image_file.tell() > MAX_IMAGE_SIZE_MB * 1024 * 1024:
            st.error(
                f"Image {image_file.name} is too large. Please upload files smaller than {MAX_IMAGE_SIZE_MB} MB."
            )
            return None
        image_file.seek(0)  # Reset to beginning
        return base64.b64encode(image_file.read()).decode("utf-8")
    except Exception as e:
        st.error(f"Error encoding {image_file.name}: {str(e)}")
        return None


# Function to create DOCX (improvement: added error handling and logging)
def create_docx(test_cases_text, uploaded_files):
    try:
        doc = Document()
        title = doc.add_heading("Generated Test Cases", 0)
        title.alignment = 1
        doc.add_paragraph(
            f"Generated on: {st.session_state.get('generation_date', 'N/A')}"
        )
        doc.add_paragraph()

        if uploaded_files:
            doc.add_heading("Source Screenshots:", level=1)
            for i, image_file in enumerate(uploaded_files, 1):
                image_file.seek(0)
                try:
                    image_stream = BytesIO(image_file.read())
                    doc.add_picture(image_stream, width=Inches(4))
                    caption_para = doc.add_paragraph(
                        f"Screenshot {i}: {image_file.name}"
                    )
                    caption_para.alignment = 1
                    doc.add_paragraph()
                except Exception as e:
                    doc.add_paragraph(
                        f"{i}. {image_file.name} (Image could not be inserted: {str(e)})"
                    )

        doc.add_heading("Test Cases:", level=1)
        lines = test_cases_text.split("\n")
        for line in lines:
            if line.strip():
                if any(
                    keyword in line
                    for keyword in [
                        "Test Case",
                        "Description:",
                        "Pre-conditions:",
                        "Testing Steps:",
                        "Expected Result:",
                    ]
                ):
                    if "Test Case" in line:
                        doc.add_heading(line.strip(), level=2)
                    else:
                        para = doc.add_paragraph()
                        run = para.add_run(line.strip())
                        run.bold = True
                else:
                    doc.add_paragraph(line.strip())

        docx_buffer = BytesIO()
        doc.save(docx_buffer)
        docx_buffer.seek(0)
        return docx_buffer
    except Exception as e:
        st.error(f"Error creating DOCX: {str(e)}")
        return None


# Page config (unchanged)
st.set_page_config(page_title="Test Case Generator", page_icon="🤖", layout="wide")

st.title("IMG2Case")
st.markdown("---")

# Image upload with validation
uploaded_files = st.file_uploader(
    "Upload Screenshot(s) or image(s)",
    type=["png", "jpeg", "jpg"],
    accept_multiple_files=True,
)

st.markdown("---")

# Optional text input (improvement: added placeholder for better UX)
optional_text = st.text_area(
    "Optional Text Context:",
    placeholder="Enter any additional context for the test cases (e.g., app type, specific features)...",
)

# Sidebar for images (unchanged)
if uploaded_files:
    st.sidebar.header("Uploaded Images")
    for image_file in uploaded_files:
        st.sidebar.image(image_file, caption=image_file.name, use_container_width=True)

# Generate Button with improved logic
generate_button_disabled = not uploaded_files
if st.button("Generate", disabled=generate_button_disabled):
    if not optional_text:
        optional_text = DEFAULT_PROMPT_CONTEXT

    # Validate and encode images (improvement: filter out invalid encodings)
    images_data = []
    for image_file in uploaded_files:
        encoded_image = encode_image_to_base64(image_file)
        if encoded_image:
            images_data.append(
                {
                    "media_type": f"image/{image_file.type.split('/')[-1]}",
                    "data": encoded_image,
                }
            )

    if not images_data:
        st.error("No valid images could be processed. Please check your uploads.")
        st.stop()

    payload = {"images": images_data, "text": optional_text}
    headers = {"Content-Type": "application/json"}

    # Improvement: Add loading indicator and timeout handling
    with st.spinner("Generating test cases... This may take a moment."):
        try:
            response = requests.post(
                API_URL, json=payload, headers=headers, timeout=60
            )  # Added timeout
            if response.status_code == 200:
                test_cases = response.json()
                st.subheader("Generated Test Cases:")
                st.write(test_cases)
                st.session_state.test_cases_result = test_cases
                st.session_state.uploaded_files_info = uploaded_files
                from datetime import datetime

                st.session_state.generation_date = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                st.success("Test cases generated successfully!")
            else:
                st.error(f"API Error: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {str(e)}")

# Download section with improvements
if st.session_state.test_cases_result:
    st.markdown("---")
    try:
        docx_buffer = create_docx(
            st.session_state.test_cases_result, st.session_state.uploaded_files_info
        )
        if docx_buffer:
            st.download_button(
                label="📄 Download Test Cases as DOCX",
                data=docx_buffer.getvalue(),
                file_name=f"test_cases_{st.session_state.generation_date.replace(':', '-').replace(' ', '_')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                type="primary",
            )
    except Exception as e:
        st.error(f"Error preparing download: {str(e)}")
