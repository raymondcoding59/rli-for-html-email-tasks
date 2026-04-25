import os
import base64
import json
import math
import re
from bs4 import BeautifulSoup
from openai import OpenAI

client = OpenAI(api_key=os.getenv("YOUR_API_KEY"))

input_path_base = "2026-04/25"
output_path_base = "2026-04/25/1"

os.makedirs(output_path_base, exist_ok=True)

# -----------------------------
# TOKEN TRACKING
# -----------------------------
token_log = []
total_tokens = 0
process_log = []

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


def log_process(item, reference, output):
    entry = {
        "process_count": len(process_log) + 1,
        "item": item,
        "reference": reference,
        "output": output
    }
    process_log.append(entry)


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


def save_process_log():
    content = "# PROCESSES\n\n"

    for entry in process_log:
        content += f"## PROCESS No. {entry['process_count']}\n"
        content += f"**Building the {entry['item']} section**\n\n\n"
        content += f"Used this reference:\n ````html\n{entry['reference']}\n````\n"
        content += f"Generated this output:\n ````html\n{entry['output']}\n````\n"

    with open(f"{output_path_base}/PROCESSES.md", "w", encoding="utf-8") as f:
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


def safe_json_loads(text):
    try:
        return json.loads(text)
    except:
        match = re.search(r'\{.*\}|\[.*\]', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except:
                pass

        cleaned = text.replace("```json", "").replace("```", "").strip()

        try:
            return json.loads(cleaned)
        except:
            print("[ERROR] Could not parse JSON.")
            return {}


# -----------------------------
# CHUNKING
# -----------------------------
def split_html_into_chunks(html):
    print("[STEP 1] Semantic chunking...")

    soup = BeautifulSoup(html, "html.parser")

    chunks = []
    for table in soup.find_all("table"):
        if len(str(table)) < 500:
            continue
        chunks.append(str(table))

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
# CHUNK SUMMARIZATION
# -----------------------------
def summarize_chunk(chunk_html):
    prompt = f"""
Analyze this email HTML chunk.

Return STRICT JSON:

{{
"type": "hero | text | split | grid | footer | button | image",
"layout": "single | two-column | grid",
"elements": ["image","heading","body","button","list"],
"image_position": "top | left | right | background | none",
"has_button": true/false
}}

HTML:
{chunk_html[:2000]}
"""

    res = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    log_tokens("chunk_summary", res)

    try:
        return json.loads(res.choices[0].message.content)
    except:
        return {"type": "unknown"}


# -----------------------------
# EMBEDDINGS
# -----------------------------
def embed_chunks(chunk_paths):
    print("[STEP 3] Embedding chunks...")

    embeddings = []

    for path in chunk_paths:
        content = load_file(path)
        summary = summarize_chunk(content)

        emb_input = json.dumps(summary)

        res = client.embeddings.create(
            model="text-embedding-3-small",
            input=emb_input
        )

        embeddings.append({
            "path": path,
            "embedding": res.data[0].embedding,
            "summary": summary
        })

    return embeddings


def cosine_similarity(a, b):
    return sum(x*y for x, y in zip(a, b)) / (
        math.sqrt(sum(x*x for x in a)) *
        math.sqrt(sum(y*y for y in b))
    )


def find_best_chunks(layout_item, embeddings, k=5):
    query = json.dumps(layout_item)

    query_emb = client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    ).data[0].embedding

    scored = []
    for item in embeddings:
        score = cosine_similarity(query_emb, item["embedding"])
        scored.append((score, item))

    scored.sort(reverse=True, key=lambda x: x[0])

    return [x[1]["path"] for x in scored[:k]]


# -----------------------------
# IMAGE MEMORY
# -----------------------------
def build_image_memory(html):
    print("[STEP] Building image memory...")

    soup = BeautifulSoup(html, "html.parser")

    images = []
    for img in soup.find_all("img"):
        src = img.get("src")
        width = img.get("width")

        if src:
            images.append({
                "src": src,
                "width": width
            })

    return images


# -----------------------------
# DESIGN SPEC EXTRACTION (NEW)
# -----------------------------
def extract_design_spec(image_base64):
    print("[STEP 4] Extracting full design spec...")

    prompt = """
Analyze this email design image.

Return ONLY valid JSON.

Structure:

{
  "sections": [
    {
      "type": "...",
      "layout": "...",
      "elements": ["image","heading","body","list","button"],
      "image_position": "...",
      "text_alignment": "...",
      "columns": number,

      "content": {
        "heading": "...exact text...",
        "body": "...exact text...",
        "button": "...CTA text...",
        "list_items": ["...", "..."],
        "labels": ["...", "..."],
        "image_descriptions": ["describe image content"]
      }
    }
  ]
}

RULES:
- Extract ALL visible text exactly
- Preserve capitalization
- Extract button labels exactly
- Extract list items
- Describe images briefly
- DO NOT return placeholders
- DO NOT include code fences
"""

    res = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
            ]
        }],
        temperature=0
    )

    log_tokens("design_spec_extraction", res)

    raw = res.choices[0].message.content.strip()

    save_file(f"{output_path_base}/design_spec.txt", raw)

    return safe_json_loads(raw)


# -----------------------------
# GENERATION
# -----------------------------
def generate_section(layout_item, content, reference_chunks, image_memory):
    print(f"[GENERATE] {layout_item}")

    refs = "\n\n".join(reference_chunks)

    prompt = f"""
You are an expert email developer.

GOAL:
Build a section that matches BOTH:
1. TARGET STRUCTURE
2. EXACT CONTENT

STRICT STYLE RULES:
- Preserve coding style from references
- Do NOT invent new patterns

STRUCTURE:
- Must match layout exactly

CONTENT RULES:
- Use EXACT text provided
- Do NOT write placeholder text
- Do NOT summarize
- Do NOT invent content

REFERENCE HTML:
{refs}

TARGET STRUCTURE:
{json.dumps(layout_item)}

CONTENT:
{json.dumps(content)}

IMAGE RULE:
- Match images based on description
- Reuse from:
{json.dumps(image_memory[:10])}
- Otherwise use placeholder

Return ONLY HTML.
"""

    res = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    html_output = res.choices[0].message.content.strip()

    log_tokens("generate_section", res)
    log_process(layout_item, refs, html_output)

    return html_output


# -----------------------------
# BUILD EMAIL
# -----------------------------
def build_email(reference_html, design_spec, embeddings, image_memory):
    print("[STEP 5] Building email...")

    head_part = reference_html.split("<body")[0]
    final_html = head_part + "<body>\n"

    for section in design_spec.get("sections", []):
        layout_item = {k: section[k] for k in section if k != "content"}

        best_paths = find_best_chunks(layout_item, embeddings)
        reference_chunks = [load_file(p) for p in best_paths]

        section_html = generate_section(
            layout_item,
            section.get("content", {}),
            reference_chunks,
            image_memory
        )

        final_html += section_html + "\n\n"

    final_html += "</body></html>"

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

    image_memory = build_image_memory(reference_html)

    image_base64 = encode_image(design_path)
    design_spec = extract_design_spec(image_base64)

    final_html = build_email(reference_html, design_spec, embeddings, image_memory)

    save_file(f"{output_path_base}/output.html", final_html)

    save_readme()
    save_process_log()

    print("\n✅ DONE")


# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    run_pipeline(
        f"{input_path_base}/reference-code.html",
        f"{input_path_base}/new-design.png"
    )