import json
import boto3
import botocore.config

# Initialize AWS client for Bedrock
bedrock_client = boto3.client(
    "bedrock-runtime",
    region_name="us-east-1",
    config=botocore.config.Config(read_timeout=300, retries={"max_attempts": 3}),
)

prompt = """
I am an experienced software tester tasked with creating comprehensive test cases for various functionalities of a digital product. I will provide you with multiple examples of test cases. Please follow these examples to generate similar detailed and professional test cases for the features visible in the provided screenshots.
For each test case, include the following:
Description: What the test case is about and which functionality is being tested.
Pre-conditions: Any prerequisites or setups needed before the test can be executed.
Testing Steps: Step-by-step instructions on how to perform the test.
Expected Result: The outcome that indicates the feature is working as intended.

Example Test Case 1: Search Functionality in a Bus Booking App
Description: Verifies that the search functionality in the bus booking app returns results based on selected cities and dates.
Pre-conditions:
The user must be logged in to the app.
The user must have selected the source and destination cities from the dropdown options.
The user must have chosen a date for the trip.
Testing Steps:
Navigate to the 'Search' page.
Select 'Chennai' from the 'From' dropdown.
Select 'Bangalore' from the 'To' dropdown.
Click on the 'Date' field and choose '30th September.'
Click the 'Search' button.
Expected Result: The app displays a list of available buses for the chosen route on the selected date.

Example Test Case 2: User Login Functionality
Description: Ensures that the user can successfully log in with valid credentials.
Pre-conditions:
The app must be installed on the user’s device.
The user must have an active account with a valid username and password.
Testing Steps:
Open the app on the device.
Navigate to the login screen.
Enter a valid username in the 'Username' field.
Enter the correct password in the 'Password' field.
Click on the 'Login' button.
Expected Result: The user is redirected to the home screen, and a welcome message with the user's name is displayed.

Example Test Case 3: Adding an Item to Cart in an E-Commerce App
Description: Checks that an item can be added to the shopping cart successfully.
Pre-conditions:
The user must be logged in to their account.
The app should have products listed in the catalog.
The item to be added must be in stock.
Testing Steps:
Navigate to the 'Products' page.
Select a category, e.g., 'Electronics.'
Choose a specific product, e.g., 'Wireless Headphones.'
Click on the 'Add to Cart' button.
Expected Result: The item is added to the cart, and the cart icon displays the updated number of items.

Example Test Case 4: Profile Update Functionality
Description: Verifies that a user can update their profile information, such as their email address and phone number.
Pre-conditions:
The user must be logged in to the app.
The user must be on the 'Profile' page.
Testing Steps:
Navigate to the 'Profile' page.
Click on the 'Edit Profile' button.
Update the 'Email' field with a new valid email address.
Update the 'Phone Number' field with a new valid phone number.
Click on the 'Save Changes' button.
Expected Result: A confirmation message is displayed, and the profile information is updated accordingly.

Now, using the provided screenshots, generate detailed test cases following the format and structure of these examples. Ensure each test case includes a clear Description, Pre-conditions, Testing Steps, and Expected Result.
"""


def lambda_handler(event, context):
    # Extract images from the input payload
    try:
        body = json.loads(event["body"])
        images = body.get("images", [])
        if not images:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "No images provided."}),
            }

        # Prepare the request for Claude 3 with multiple images
        content_array = []
        for image in images:
            content_array.append(
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": image[
                            "media_type"
                        ],  # e.g., 'image/png' or 'image/jpeg'
                        "data": image["data"],  # Base64-encoded image string
                    },
                }
            )

        # Add a text prompt
        content_array.append(
            {"type": "text", "text": f"{prompt} Additional Context:{body['text']}"}
        )

        # Define the API request payload
        payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "messages": [{"role": "user", "content": content_array}],
        }

        # Call the Claude 3 Text and Vision model using Bedrock API
        response = bedrock_client.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps(payload),
        )

        # Parse the response
        response_body = response["body"].read().decode("utf-8")
        model_output = json.loads(response_body)
        model_output = model_output["content"][0]["text"]
        return {"statusCode": 200, "body": json.dumps(model_output)}

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
