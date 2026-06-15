
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

B. Where it appears in the email.

C. What visual role it plays.

D. Generate a semantic fingerprint optimized for future vector search / RAG retrieval.

E. Generate retrieval keywords.

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

 