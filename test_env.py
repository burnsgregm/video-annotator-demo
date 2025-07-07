from dotenv import load_dotenv
import os

load_dotenv()

print("ROBOFLOW_API_KEY:", os.getenv("ROBOFLOW_API_KEY"))
print("ROBOFLOW_MODEL:  ", os.getenv("ROBOFLOW_MODEL"))
print("ROBOFLOW_VERSION:", os.getenv("ROBOFLOW_VERSION"))