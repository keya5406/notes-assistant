import os
from dotenv import  load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("API_KEY")

genai.configure(api_key=api_key)

try:
    model = genai.GenerativeModel("gemini-2.5-flash-lite")
    response = model.generate_content("Hello Gemini.")
    print("Response: ", response)
except Exception as e:
    print("Error:", e)

