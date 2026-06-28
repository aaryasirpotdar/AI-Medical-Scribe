
from dotenv import load_dotenv
import os
import google.generativeai as genai
import json
import re 

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel("gemini-2.5-flash")
def extract_medical_info(transcript):

    prompt = f"""
    Extract the following information from the medical transcript:

    - Symptoms
    - Duration
    - BP
    - Medical History
    - Medicines
    - Tests

    Return ONLY JSON.

    Transcript:
    {transcript}
    """

    response = model.generate_content(prompt)

    # DEBUG
    print("\n===== RAW GEMINI RESPONSE =====")
    print(response.text)
    print("===============================\n")

    text = response.text

    text = re.sub(r"```json|```", "", text).strip()

    data = json.loads(text)

    print("EXTRACTED DATA:")
    print(data)

    return data