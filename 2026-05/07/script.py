import base64
import json
import math
import os
import re
from bs4 import BeautifulSoup
from collections import Counter
from openai import OpenAI


# paths and files
API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    raise RuntimeError("Set up OpenAI API key before running this script")
client = OpenAI(api_key = API_KEY)


#helper functions and main functions


def generate_section():
    

def build_email():
    

def run_pipeline():
    



if __name__ == "__main__":
    run_pipeline()