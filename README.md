# IMG2Case: Screenshot-Based Test Case Generator

## Overview

**IMG2Case** is a tool designed to automatically generate detailed software test cases from screenshots of digital products. By leveraging Google Gemini's generative AI capabilities, the app analyzes uploaded images and optional context to produce professional test cases in a structured format.

## Features

- Upload one or more screenshots (PNG, JPEG, JPG).
- Optionally provide additional textual context for more accurate test case generation.
- Generates test cases with:
  - Description
  - Pre-conditions
  - Testing Steps
  - Expected Result
- Clean, interactive Streamlit frontend.
- Flask backend integrates with Google Gemini API.

## Architecture

- **Frontend:** Streamlit (`app.py`)
  - Handles image upload, context input, and displays generated test cases.
- **Backend:** Flask (`gemini_backend.py`)
  - Receives images and context, calls Gemini API, returns generated test cases.

## How It Works

1. **User uploads screenshots** via the Streamlit interface.
2. **Optional context** can be provided to guide test case generation.
3. Images and context are sent to the Flask backend.
4. The backend prepares the prompt and media, calls Gemini API, and returns the generated test cases.
5. Test cases are displayed in the Streamlit app.

## Getting Started

### Prerequisites

- Python 3.8+
- [Google Gemini API key](https://ai.google.dev/)
- [OpenAI API key](https://platform.openai.com/) 
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```

### Environment Setup

Create a `.env` file in the project root (refer [.env.example](.env.example)):
```
GEMINI_API_KEY=your_gemini_api_key_here
```

### Running the Application

1. **Start the backend:**
   ```bash
   python gemini_backend.py
   ```
   The Flask server will run on `http://localhost:8000`.

2. **Start the frontend:**
   ```bash
   streamlit run app.py
   ```
   Access the app in your browser at `http://localhost:8501`.

## API Endpoint

- **POST** `/gemini-generate`
  - **Payload:**
    ```json
    {
      "images": [
        {
          "media_type": "image/png",
          "data": "<base64-encoded-image>"
        }
      ],
      "text": "Optional context"
    }
    ```
  - **Response:** Generated test cases in text format.

## Example Usage

1. Upload screenshots of your app or website.
2. Optionally add context (if necessary)
3. Click **Generate**.
4. Review the generated test cases in the output section.

## Notes

- Ensure your Gemini API key is valid and has sufficient quota.
- The backend expects images in base64 format and a valid media type.
- For best results, provide clear screenshots and relevant context.

## License

This project is licensed for educational and internal use. Please check [LICENSE](LICENSE)