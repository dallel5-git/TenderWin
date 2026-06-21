import os
from dotenv import load_dotenv
from smolagents import LiteLLMModel
load_dotenv('/home/oussama/Bureau/tenderwin_project/.env')
model = LiteLLMModel(
    model_id=os.getenv("MODEL_ID", "gemini/gemini-2.5-flash"),
    api_key=os.getenv("GEMINI_API_KEY"),
)
try:
    print(model([{"role": "user", "content": "Hi"}]))
except Exception as e:
    print("ERROR IS:", e)
