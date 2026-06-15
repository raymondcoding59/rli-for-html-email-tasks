import os
import json
import base64
import requests
from bs4 import BeautifulSoup
from openai import OpenAI

ROOT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

REFERENCE_DESIGN_PATH = os.path.join(
    ROOT_DIR,
    "reference-design.png"
)

API_KEY = (
    os.getenv("OPENAI_API_KEY")
    or os.getenv("YOUR_API_KEY")
)

if not API_KEY:
    raise RuntimeError(
        "Set OPENAI_API_KEY before running this script."
    )

client = OpenAI(api_key=API_KEY)


def load_file(path):
    """Read UTF-8 text files."""
    with open(path, "r", encoding="utf-8") as file:
        return file.read()


html_snippet = load_file(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "../14/chunks/chunk_0.html"
        )
    )
)


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


def extract_image_urls(html_snippet):
    """
    Extract image URLs from HTML.
    """
    soup = BeautifulSoup(html_snippet, "html.parser")

    urls = []

    for img in soup.find_all("img"):
        src = img.get("src")

        if src:
            urls.append(src)

    return urls


def analyse_email_snippet(
    design_image_path,
    html_snippet
):
    """
    Analyze an HTML chunk against a full email design.

    Returns JSON:
    {
        component_type,
        location_in_design,
        visual_description,
        purpose,
        keywords,
        fingerprint,
        rag_text
    }
    """

    # Load design image
    with open(design_image_path, "rb") as f:
        design_b64 = base64.b64encode(
            f.read()
        ).decode("utf-8")

    design_data_url = (
        f"data:image/png;base64,{design_b64}"
    )

    image_urls = extract_image_urls(html_snippet)

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

B. Where it appears in the email.

C. What visual role it plays.

D. Generate a semantic fingerprint optimized for future vector search / RAG retrieval.

E. Generate retrieval keywords.

Return ONLY valid JSON.

HTML SNIPPET:

{html_snippet}
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
        model="gpt-4.1-mini",
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
                        "location_in_design": {
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
                        "location_in_design",
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


if __name__ == "__main__":

    result = analyse_email_snippet(
        design_image_path=REFERENCE_DESIGN_PATH,
        html_snippet=html_snippet
    )

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        )
    )