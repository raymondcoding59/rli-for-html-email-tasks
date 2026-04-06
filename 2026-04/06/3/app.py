import os
import base64
import json
import math
from openai import OpenAI

client = OpenAI(api_key=os.getenv("YOUR_API_KEY"))

input_path_base = "2026-04/06"
output_path_base = "2026-04/06/3"

os.makedirs(output_path_base, exist_ok=True)


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
# SAFER HTML CHUNKING (TABLE-BASED)
# -----------------------------
def split_html_into_chunks(html):
    parts = html.split("</table>")
    chunks = []

    for part in parts:
        part = part.strip()
        if part:
            chunks.append(part + "</table>")

    if not chunks:
        return [html]

    return chunks


# -----------------------------
# SAVE CHUNKS
# -----------------------------
def save_chunks(chunks):
    folder = f"{output_path_base}/chunks"
    os.makedirs(folder, exist_ok=True)

    paths = []

    for i, chunk in enumerate(chunks):
        path = f"{folder}/chunk_{i}.html"
        save_file(path, chunk)
        paths.append(path)

    save_file(f"{output_path_base}/chunks_index.json", json.dumps(paths, indent=2))

    return paths


# -----------------------------
# EMBEDDINGS
# -----------------------------
def embed_chunks(chunk_paths):
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

    save_file(f"{output_path_base}/embeddings.json", json.dumps(embeddings))

    return embeddings


# -----------------------------
# COSINE SIMILARITY
# -----------------------------
def cosine_similarity(a, b):
    return sum(x * y for x, y in zip(a, b)) / (
        math.sqrt(sum(x * x for x in a)) *
        math.sqrt(sum(y * y for y in b))
    )


# -----------------------------
# FIND BEST CHUNK
# -----------------------------
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
    res = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": """
Extract a MINIMAL layout.

Return JSON array like:
[
  "hero image",
  "heading: ...",
  "paragraph: ...",
  "button: ...",
  "image",
  "section: ..."
]

Be concise.
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

    layout = res.choices[0].message.content.strip()

    save_file(f"{output_path_base}/layout.json", layout)

    return layout


# -----------------------------
# EDIT CHUNK (STRICT STRUCTURE LOCK)
# -----------------------------
def edit_chunk_file(chunk_path, layout_item):
    chunk_html = load_file(chunk_path)

    prompt = f"""
You are editing an email HTML template.

ABSOLUTE RULES:
- Do NOT generate new structure
- Do NOT add new tables, divs, or sections
- Do NOT remove wrappers
- ONLY replace text, images, and links
- Preserve ALL attributes, styles, classes

IMAGE RULE:
Use https://placehold.co/600x400.png for new images

IMPORTANT:
Output MUST match structure exactly.

HTML:
{chunk_html}

CHANGE:
{layout_item}

Return ONLY raw HTML.
NO markdown.
"""

    res = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    html = res.choices[0].message.content.strip()
    html = html.replace("```html", "").replace("```", "").strip()

    return html


# -----------------------------
# BUILD EMAIL (STRUCTURE-PRESERVING)
# -----------------------------
def build_email(reference_html, layout, embeddings):
    layout_items = json.loads(layout)

    final_html = reference_html

    mapping_debug = []

    for item in layout_items:
        chunk_path = find_best_chunk(item, embeddings)

        original_chunk = load_file(chunk_path)
        edited_chunk = edit_chunk_file(chunk_path, item)

        if original_chunk in final_html:
            final_html = final_html.replace(original_chunk, edited_chunk)

        mapping_debug.append({
            "layout_item": item,
            "chunk_used": chunk_path
        })

    save_file(
        f"{output_path_base}/mapping_debug.json",
        json.dumps(mapping_debug, indent=2)
    )

    return final_html


# -----------------------------
# PIPELINE
# -----------------------------
def run_pipeline(reference_path, design_path):
    reference_html = load_file(reference_path)

    # 1. Split
    chunks = split_html_into_chunks(reference_html)
    chunk_paths = save_chunks(chunks)

    # 2. Embed
    embeddings = embed_chunks(chunk_paths)

    # 3. Layout
    image_base64 = encode_image(design_path)
    layout = extract_layout(image_base64)

    # 4. Build (critical fix: in-place editing)
    final_html = build_email(reference_html, layout, embeddings)

    # 5. Save
    save_file(f"{output_path_base}/output.html", final_html)

    return final_html


# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    run_pipeline(
        f"{input_path_base}/reference-code.html",
        f"{input_path_base}/new-design.png"
    )

    print("✅ Done. Output saved to output.html")