import streamlit as st
import requests
import base64
from docx import Document
from docx.shared import Inches
from io import BytesIO

if "test_cases_result" not in st.session_state:
    st.session_state.test_cases_result = None
if "uploaded_files_info" not in st.session_state:
    st.session_state.uploaded_files_info = None
if "generation_date" not in st.session_state:
    st.session_state.generation_date = None


# Function to encode images to Base64
def encode_image_to_base64(image_file):
    return base64.b64encode(image_file.read()).decode("utf-8")


# Function to create docx
def create_docx(test_cases_text, uploaded_files):
    doc = Document()

    # Add title
    title = doc.add_heading("Generated Test Cases", 0)
    title.alignment = 1  # Center alignment

    # Add date
    doc.add_paragraph(f"Generated on: {st.session_state.get('generation_date', 'N/A')}")
    doc.add_paragraph()

    # Add uploaded images
    if uploaded_files:
        doc.add_heading("Source Screenshots:", level=1)
        for i, image_file in enumerate(uploaded_files, 1):
            # Reset file pointer to beginning
            image_file.seek(0)

            # Add image to document
            try:
                # Create a BytesIO object from the uploaded file
                image_stream = BytesIO(image_file.read())

                # Add the image with a reasonable width (adjust as needed)
                doc.add_picture(image_stream, width=Inches(4))

                # Add caption
                caption_para = doc.add_paragraph(f"Screenshot {i}: {image_file.name}")
                caption_para.alignment = 1  # Center alignment

                # Add some space after each image
                doc.add_paragraph()

            except Exception as e:
                # Fallback to text if image insertion fails
                doc.add_paragraph(
                    f"{i}. {image_file.name} (Image could not be inserted: {str(e)})"
                )

        doc.add_paragraph()

    # Add test cases content
    doc.add_heading("Test Cases:", level=1)

    # Split content by test cases (assuming each test case starts with "Test Case" or similar)
    lines = test_cases_text.split("\n")
    for line in lines:
        if line.strip():
            # Check if it's a heading (contains "Test Case", "Description", etc.)
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

    # Save to BytesIO
    docx_buffer = BytesIO()
    doc.save(docx_buffer)
    docx_buffer.seek(0)

    return docx_buffer


# Page config
st.set_page_config(
    page_title="Test Case Generator",
    page_icon="🤖",
    layout="wide",
)

# Streamlit App
st.title("IMG2Case")
st.markdown("---")

# Image upload
uploaded_files = st.file_uploader(
    "Upload Screenshot(s) or image(s)",
    type=["png", "jpeg", "jpg"],
    accept_multiple_files=True,
)

st.markdown("---")

# Optional text input for context (to be removed later)
optional_text = st.text_area(
    "Optional Text Context:",
    placeholder="Enter any additional context for the test cases...",
)

# Sidebar to display uploaded images
if uploaded_files:
    st.sidebar.header("Uploaded Images")
    for image_file in uploaded_files:
        st.sidebar.image(image_file, caption=image_file.name, use_container_width=True)

# Generate Button - Enabled only if images are uploaded
generate_button_disabled = not uploaded_files

# Generate Button
if st.button("Generate", disabled=generate_button_disabled):
    if not optional_text:
        optional_text = "None"

    # Prepare the payload
    images_data = []
    for image_file in uploaded_files:
        # Reset file pointer for encoding
        image_file.seek(0)
        encoded_image = encode_image_to_base64(image_file)
        images_data.append(
            {
                "media_type": f"image/{image_file.type.split('/')[-1]}",
                "data": encoded_image,
            }
        )
        # print(f"Encoded image: {encoded_image}...")

    # Construct payload for the API call
    payload = {"images": images_data, "text": optional_text}

    # Make API call to Gemini
    api_url = "http://localhost:8000/gemini-generate"
    headers = {"Content-Type": "application/json"}

    response = requests.post(api_url, json=payload, headers=headers)

    # Handle the response
    if response.status_code == 200:
        test_cases = response.json()
        st.subheader("Generated Test Cases:")
        st.write(test_cases)
        st.session_state.test_cases_result = test_cases
        st.session_state.uploaded_files_info = uploaded_files
        from datetime import datetime

        st.session_state.generation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    else:
        st.error(f"Error: {response.status_code} - {response.text}")

if st.session_state.test_cases_result:
    st.markdown("---")

    # Create download button that directly downloads
    try:
        docx_buffer = create_docx(
            st.session_state.test_cases_result, st.session_state.uploaded_files_info
        )

        st.download_button(
            label="📄 Download Test Cases as DOCX",
            data=docx_buffer.getvalue(),
            file_name=f"test_cases_{st.session_state.generation_date.replace(':', '-').replace(' ', '_')}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            type="primary",
        )

    except Exception as e:
        st.error(f"Error creating DOCX file: {str(e)}")
