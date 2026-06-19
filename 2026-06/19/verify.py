from openai import OpenAI
import json

client = OpenAI()


def verify_and_correct_fingerprints(
    fingerprints,
    design_image_base64,
    model="gpt-4.1"
):

    review_payload = []

    total = len(fingerprints)

    for idx, fingerprint in enumerate(fingerprints):
        review_payload.append(
            {
                "chunk_index": idx,
                "position": f"{idx + 1}/{total}",
                "fingerprint": fingerprint
            }
        )

    prompt = f"""
You are reviewing fingerprints generated from chunks of an HTML email.

IMPORTANT:

- The fingerprints were generated independently and may contain mistakes.
- The chunks appear in TOP-TO-BOTTOM order in the email.
- Use the full design image and the sequence of fingerprints to infer
  the true structure of the email.
- Correct fingerprints that appear inaccurate.
- Preserve fingerprints that are already correct.
- Preserve the existing fingerprint schema and field names.
- Do not invent new schema fields.
- Return ALL fingerprints, including unchanged ones.

Return ONLY valid JSON.

Expected format:

[
  {{
    "chunk_index": 0,
    "fingerprint": {{
      ...
    }}
  }}
]

Fingerprints:

{json.dumps(review_payload, indent=2)}
"""

    response = client.responses.create(
        model=model,
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": prompt
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/png;base64,{design_image_base64}"
                    }
                ]
            }
        ]
    )

    raw_output = response.output_text.strip()

    try:
        corrected = json.loads(raw_output)
    except Exception:
        print("\n===== GPT RESPONSE =====")
        print(raw_output)
        print("========================\n")
        raise ValueError(
            "Fingerprint verification returned invalid JSON."
        )

    corrected_map = {}

    for item in corrected:
        if (
            isinstance(item, dict)
            and "chunk_index" in item
            and "fingerprint" in item
        ):
            corrected_map[item["chunk_index"]] = item["fingerprint"]

    final_fingerprints = []

    for idx, original_fp in enumerate(fingerprints):
        final_fingerprints.append(
            corrected_map.get(idx, original_fp)
        )

    return final_fingerprints


def update_saved_fingerprints(
    fingerprints,
    design_image_base64,
    save_callback,
    model="gpt-4.1"
):
    """
    Verifies fingerprints and immediately persists corrections.

    save_callback should accept:

        save_callback(corrected_fingerprints)
    """

    corrected_fingerprints = verify_and_correct_fingerprints(
        fingerprints=fingerprints,
        design_image_base64=design_image_base64,
        model=model
    )

    save_callback(corrected_fingerprints)

    return corrected_fingerprints