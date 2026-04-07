import os
import base64
import json
import math
import re
from openai import OpenAI

client = OpenAI(api_key=os.getenv("YOUR_API_KEY"))

input_path_base = "2026-04/07/2"
output_path_base = "2026-04/07/2"

os.makedirs(output_path_base, exist_ok=True)

# -----------------------------
# TOKEN TRACKING
# -----------------------------
token_log = []
total_tokens = 0


def log_tokens(step, response):
    global total_tokens

    usage = response.usage

    entry = {
        "step": step,
        "input_tokens": usage.prompt_tokens,
        "output_tokens": usage.completion_tokens,
        "total_tokens": usage.total_tokens
    }

    total_tokens += usage.total_tokens
    token_log.append(entry)


def save_readme():
    content = "# API TOKEN USAGE LOG\n\n"

    for entry in token_log:
        content += f"## {entry['step']}\n"
        content += f"- Input: {entry['input_tokens']}\n"
        content += f"- Output: {entry['output_tokens']}\n"
        content += f"- Total: {entry['total_tokens']}\n\n"

    content += f"# GRAND TOTAL: {total_tokens}\n"

    with open(f"{output_path_base}/README.md", "w") as f:
        f.write(content)


# -----------------------------
# HELPERS
# -----------------------------
def save_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def load_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def encode_image(image_path):
    with open(image_path, "rb") as img:
        return base64.b64encode(img.read()).decode("utf-8")


# -----------------------------
# JSON SAFETY FIX
# -----------------------------
def safe_json_loads(text):
    try:
        return json.loads(text)
    except:
        print("[WARN] Invalid JSON from model. Attempting repair...")

        lines = text.strip().split("\n")
        cleaned = [l.strip("-• ").strip() for l in lines if l.strip()]

        return cleaned


# -----------------------------
# CHUNKING
# -----------------------------
def split_html_into_chunks(html):
    print("[STEP 1] Splitting HTML...")

    parts = html.split("</table>")
    chunks = []

    for part in parts:
        part = part.strip()
        if part:
            chunks.append(part + "</table>")

    return chunks if chunks else [html]


def save_chunks(chunks):
    print("[STEP 2] Saving chunks...")

    folder = f"{output_path_base}/chunks"
    os.makedirs(folder, exist_ok=True)

    paths = []

    for i, chunk in enumerate(chunks):
        path = f"{folder}/chunk_{i}.html"
        save_file(path, chunk)
        paths.append(path)

    return paths


# -----------------------------
# EMBEDDINGS
# -----------------------------
def embed_chunks(chunk_paths):
    print("[STEP 3] Embedding chunks...")

    embeddings = []

    for path in chunk_paths:
        content = load_file(path)

        res = client.embeddings.create(
            model="text-embedding-3-small",
            input=content[:2000]
        )

        embeddings.append({
            "path": path,
            "embedding": res.data[0].embedding
        })

    return embeddings


def cosine_similarity(a, b):
    return sum(x*y for x, y in zip(a, b)) / (
        math.sqrt(sum(x*x for x in a)) *
        math.sqrt(sum(y*y for y in b))
    )


def find_best_chunk(layout_item, embeddings):
    query_emb = client.embeddings.create(
        model="text-embedding-3-small",
        input=layout_item
    ).data[0].embedding

    best = None
    best_score = -1

    for item in embeddings:
        score = cosine_similarity(query_emb, item["embedding"])
        if score > best_score:
            best = item
            best_score = score

    return best["path"]


# -----------------------------
# LAYOUT EXTRACTION
# -----------------------------
def extract_layout(image_base64):
    print("[STEP 4] Extracting layout...")

    res = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": """
Return STRICT JSON array only.

Example:
["hero image", "heading: text", "button: buy"]

NO explanation.
NO text outside JSON.
"""},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
            ]
        }],
        temperature=0
    )

    log_tokens("layout_extraction", res)

    layout = res.choices[0].message.content.strip()

    save_file(f"{output_path_base}/layout_raw.txt", layout)

    return layout


# -----------------------------
# EDIT CHUNK
# -----------------------------
def edit_chunk_file(chunk_path, layout_item):
    print(f"[EDIT] {layout_item}")

    chunk_html = load_file(chunk_path)

    prompt = f"""
Edit this HTML.

STRICT:
- DO NOT change structure
- ONLY replace content

IMAGE RULE:
Replace ALL images with:
https://placehold.co/{{WIDTH}}x{{HEIGHT}}.png

WIDTH = from width attribute

HTML:
{chunk_html}

CHANGE:
{layout_item}

Return HTML only.
"""

    res = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    log_tokens("edit_chunk", res)

    return res.choices[0].message.content.strip()


# -----------------------------
# PLACEHOLDER ENFORCER
# -----------------------------
def enforce_placeholders(html):
    print("[STEP 5] Enforcing placeholders...")

    def replace_img(match):
        tag = match.group(0)

        width_match = re.search(r'width="(\d+)"', tag)
        width = width_match.group(1) if width_match else "600"

        return re.sub(
            r'src="[^"]+"',
            f'src="https://placehold.co/{width}x{width}.png"',
            tag
        )

    return re.sub(r'<img[^>]+>', replace_img, html)


# -----------------------------
# BUILD EMAIL
# -----------------------------
def build_email(reference_html, layout, embeddings):
    print("[STEP 6] Building email...")

    layout_items = safe_json_loads(layout)

    final_html = reference_html

    for item in layout_items:
        chunk_path = find_best_chunk(item, embeddings)

        original_chunk = load_file(chunk_path)
        edited_chunk = edit_chunk_file(chunk_path, item)

        if original_chunk in final_html:
            final_html = final_html.replace(original_chunk, edited_chunk)

    final_html = enforce_placeholders(final_html)

    return final_html


# -----------------------------
# PIPELINE
# -----------------------------
def run_pipeline(reference_path, design_path):
    print("🚀 STARTING PIPELINE\n")

    reference_html = load_file(reference_path)

    chunks = split_html_into_chunks(reference_html)
    chunk_paths = save_chunks(chunks)

    embeddings = embed_chunks(chunk_paths)

    image_base64 = encode_image(design_path)
    layout = extract_layout(image_base64)

    final_html = build_email(reference_html, layout, embeddings)

    save_file(f"{output_path_base}/output.html", final_html)

    save_readme()

    print("\n✅ DONE")


# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    run_pipeline(
        f"{input_path_base}/reference-code.html",
        f"{input_path_base}/new-design.png"
    )