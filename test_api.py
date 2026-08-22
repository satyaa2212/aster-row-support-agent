import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# List se latest flash model use kar rahe hain
model = genai.GenerativeModel('models/gemini-3.7-flash')

response = model.generate_content("Say hello in one word")
print(response.text)