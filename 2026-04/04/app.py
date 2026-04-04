import base64
from openai import OpenAI

client = OpenAI(api_key="YOUR_API_KEY")


# -----------------------------
# 1. LOAD FILES
# -----------------------------
def load_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def encode_image(image_path):
    with open(image_path, "rb") as img:
        return base64.b64encode(img.read()).decode("utf-8")


# -----------------------------
# 2. STYLE DNA EXTRACTION
# -----------------------------
def extract_style(reference_html):
    prompt = f"""
Analyze this email HTML and extract the developer's coding style.

Return JSON with:
- components (button, image, text, section)
- structure patterns
- spacing rules
- fonts and colors
- strict rules that must not be broken

HTML:
{reference_html}
"""

    res = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return res.choices[0].message.content


# -----------------------------
# 3. DESIGN → LAYOUT (VISION)
# -----------------------------
def extract_layout(image_base64):
    res = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": """
Analyze this email design image and return a structured JSON layout.

Include:
- sections
- headings
- paragraphs
- buttons
- images
- grouping
Return JSON only.
"""},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        temperature=0
    )

    return res.choices[0].message.content


# -----------------------------
# 4. GENERATE HTML
# -----------------------------
def generate_html(style_dna, layout_json):
    prompt = f"""
You are an expert email developer.

STRICT RULES:
- Follow the exact coding style, nesting, and structure
- Use table-based layouts only
- Match spacing, fonts, and patterns exactly
- Do NOT simplify

Style DNA:
{style_dna}

Layout:
{layout_json}

Generate full email HTML.
"""

    res = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return res.choices[0].message.content


# -----------------------------
# 5. VALIDATE + FIX LOOP
# -----------------------------
def validate_html(html, style_dna):
    prompt = f"""
Check this HTML against the style rules.

Return a list of violations or "OK".

Style DNA:
{style_dna}

HTML:
{html}
"""

    res = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return res.choices[0].message.content


def fix_html(html, issues):
    prompt = f"""
Fix the HTML based on these issues.

Issues:
{issues}

HTML:
{html}
"""

    res = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return res.choices[0].message.content


# -----------------------------
# 6. MAIN PIPELINE
# -----------------------------
def run_pipeline(reference_path, design_path):
    print("🔬 Extracting style...")
    reference_html = load_file(reference_path)
    style_dna = extract_style(reference_html)

    print("👁️ Reading design...")
    image_base64 = encode_image(design_path)
    layout = extract_layout(image_base64)

    print("🏗️ Generating HTML...")
    html = generate_html(style_dna, layout)

    print("🔁 Validating...")
    for i in range(3):  # max 3 refinement loops
        issues = validate_html(html, style_dna)
        if "OK" in issues:
            break
        html = fix_html(html, issues)

    return html


# -----------------------------
# 7. RUN
# -----------------------------
if __name__ == "__main__":
    output_html = run_pipeline(
        "reference-code.html",
        "new-design.png"
    )

    with open("output.html", "w", encoding="utf-8") as f:
        f.write(output_html)

    print("✅ Done! Saved as output.html")