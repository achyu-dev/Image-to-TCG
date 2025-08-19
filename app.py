import streamlit as st
import requests
import base64


# Function to encode images to Base64
def encode_image_to_base64(image_file):
    return base64.b64encode(image_file.read()).decode("utf-8")


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
    else:
        st.error(f"Error: {response.status_code} - {response.text}")
