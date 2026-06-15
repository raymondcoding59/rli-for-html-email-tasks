import base64
import json
import math
import os
import re
import time
import requests
from bs4 import BeautifulSoup
from collections import Counter
from openai import OpenAI
from openai import RateLimitError




ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EXPERIMENT_DIR = os.path.dirname(__file__)
REFERENCE_PATH = os.path.join(ROOT_DIR, "reference-code.html")
REFERENCE_DESIGN_PATH = os.path.join(ROOT_DIR, "reference-design.png")
DESIGN_PATH = os.path.join(ROOT_DIR, "new-design.png")
TARGET_PATH = os.path.join(ROOT_DIR, "target-generated-code.html")
OUTPUT_PATH = os.path.join(EXPERIMENT_DIR, "output.html")
DESIGN_SPEC_PATH = os.path.join(EXPERIMENT_DIR, "design_spec.txt")
NORMALIZED_SPEC_PATH = os.path.join(EXPERIMENT_DIR, "design_spec.normalized.json")
README_PATH = os.path.join(EXPERIMENT_DIR, "README.md")
PROCESSES_PATH = os.path.join(EXPERIMENT_DIR, "PROCESSES.md")
CHUNKS_DIR = os.path.join(EXPERIMENT_DIR, "chunks")
PROMPTS_DIR = os.path.join(EXPERIMENT_DIR, "prompts")

API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("YOUR_API_KEY")
if not API_KEY:
    raise RuntimeError("Set OPENAI_API_KEY before running this script.")

client = OpenAI(api_key=API_KEY)

os.makedirs(EXPERIMENT_DIR, exist_ok=True)
os.makedirs(CHUNKS_DIR, exist_ok=True)


def save_file(path, content):
    """Write UTF-8 text artifacts into the experiment folder."""
    with open(path, "w", encoding="utf-8") as file:
        file.write(content)


def load_file(path):
    """Read UTF-8 text inputs or artifacts."""
    with open(path, "r", encoding="utf-8") as file:
        return file.read()


def with_retries(api_call, max_retries=6):
    """Retry OpenAI requests with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return api_call()

        except RateLimitError:
            if attempt == max_retries - 1:
                raise

            wait_time = min(2 ** attempt, 20)

            print(
                f"[RATE LIMIT] Waiting {wait_time}s before retry "
                f"(attempt {attempt + 1}/{max_retries})"
            )

            time.sleep(wait_time)

def image_url_to_data_url(url):
    """
    Download an image and convert it to a data URL
    suitable for OpenAI vision input.
    """
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    content_type = response.headers.get(
        "content-type",
        "image/jpeg"
    )

    encoded = base64.b64encode(
        response.content
    ).decode("utf-8")

    return f"data:{content_type};base64,{encoded}"


def extract_image_urls(chunk_html):
    """
    Extract image URLs from HTML.
    """
    soup = BeautifulSoup(chunk_html, "html.parser")

    urls = []

    for img in soup.find_all("img"):
        src = img.get("src")

        if src:
            urls.append(src)

    return urls



def build_chunk_fingerprint(chunk_html, index, design_image_path):

    # Load design image
    with open(design_image_path, "rb") as f:
        design_b64 = base64.b64encode(
            f.read()
        ).decode("utf-8")

    design_data_url = (
        f"data:image/png;base64,{design_b64}"
    )

    image_urls = extract_image_urls(chunk_html)

    prompt = f"""
You are an expert email-design analyst.

You will receive:

1. A full email design screenshot.
2. An HTML snippet extracted from that email.
3. Any images referenced by the snippet.

Your job is to determine:

A. What part of the email the snippet belongs to:
   - logo
   - preheader
   - navigation
   - hero
   - hero CTA
   - product card
   - product grid
   - photogrid
   - article block
   - content section
   - divider
   - footer
   - social section
   - legal section
   - etc.


B. What visual role it plays.

C. Generate a semantic fingerprint optimized for future vector search / RAG retrieval.

D. Generate retrieval keywords.

Return ONLY valid JSON.

HTML SNIPPET:

{chunk_html}
"""

    # Responses API content blocks
    content = [
        {
            "type": "input_text",
            "text": prompt
        },
        {
            "type": "input_image",
            "image_url": design_data_url
        }
    ]

    # Add snippet images
    for url in image_urls:
        try:
            print(f"Loading image: {url}")

            content.append(
                {
                    "type": "input_image",
                    "image_url": image_url_to_data_url(url)
                }
            )

        except Exception as e:
            print(
                f"Could not load image {url}: {e}"
            )

    response = client.responses.create(
        model="gpt-4.1",
        input=[
            {
                "role": "user",
                "content": content
            }
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "email_component_analysis",
                "schema": {
                    "type": "object",
                    "properties": {
                        "component_type": {
                            "type": "string"
                        },
                        "visual_description": {
                            "type": "string"
                        },
                        "purpose": {
                            "type": "string"
                        },
                        "keywords": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        },
                        "fingerprint": {
                            "type": "string"
                        },
                        "rag_text": {
                            "type": "string"
                        }
                    },
                    "required": [
                        "component_type",
                        "visual_description",
                        "purpose",
                        "keywords",
                        "fingerprint",
                        "rag_text"
                    ],
                    "additionalProperties": False
                }
            }
        }
    )

    # Parse JSON result
    try:
        return json.loads(
            response.output_text
        )
    except Exception:
        # Fallback parser for SDK differences
        try:
            result_text = (
                response.output[0]
                .content[0]
                .text
            )

            return json.loads(result_text)

        except Exception:
            print(response)
            raise

    




def split_html_into_chunks(html):
    """Break the reference email into reusable top-level component chunks."""
    print("Splitting reference HTML into chunks...")
    soup = BeautifulSoup(html, "html.parser")

    sections = []
    for node in soup.select("div.component-wrapper"):
        chunk_html = str(node)
        sections.append(chunk_html)

    chunk_records = []
    for index, chunk_html in enumerate(sections):
        chunk_records.append(
            {
                "index": index,
                "html": chunk_html,
                "fingerprint": build_chunk_fingerprint(chunk_html, index, design_image_path=REFERENCE_DESIGN_PATH),
            }
        )
        
        
    return chunk_records


def save_chunks(chunk_records):
    """Write every reference chunk and its fingerprint for auditability."""
    print("Saving chunks...")
    for existing in os.listdir(CHUNKS_DIR):
        existing_path = os.path.join(CHUNKS_DIR, existing)
        if os.path.isfile(existing_path):
            os.remove(existing_path)
        

    for record in chunk_records:
        html_path = os.path.join(CHUNKS_DIR, f"chunk_{record['index']}.html")
        meta_path = os.path.join(CHUNKS_DIR, f"chunk_{record['index']}.json")
        save_file(html_path, record["html"])
        save_file(meta_path, json.dumps(record["fingerprint"], indent=2))


def run_pipeline():
    """Run the full experimental pipeline and persist every required artifact."""
    print("[START]")
    reference_html = load_file(REFERENCE_PATH)
    chunk_records = split_html_into_chunks(reference_html)
    save_chunks(chunk_records)
    print("[DONE]")


if __name__ == "__main__":
    run_pipeline()
