import base64 
import json
import math
import os
import re
from bs4 import BeautifulSoup
from collections import Counter
from openai import OpenAI

# PATHS

API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("YOUR_API_KEY")
if not API_KEY:
     raise RuntimeError("Set OPENAI_API_KEY before running this script.")

client = OpenAI(api_key = API_KEY)

# helper functions & main fuctions

if __name__ == "__main__": 
    run_pipeline()