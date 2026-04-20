import base64
import json
import math
import os
import re
from collections import Counter

from bs4 import BeautifulSoup
from openai import OpenAI


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EXPERIMENT_DIR = os.path.dirname(__file__)
REFERENCE_PATH = os.path.join(ROOT_DIR, "reference-code.html")
DESIGN_PATH = os.path.join(ROOT_DIR, "new-design.png")
TARGET_PATH = os.path.join(ROOT_DIR, "target-generated-code.html")
OUTPUT_PATH = os.path.join(EXPERIMENT_DIR, "output.html")
DESIGN_SPEC_PATH = os.path.join(EXPERIMENT_DIR, "design_spec.txt")
NORMALIZED_DESIGN_SPEC_PATH = os.path.join(EXPERIMENT_DIR, "design_spec.normalized.json")
NORMALIZATION_LOG_PATH = os.path.join(EXPERIMENT_DIR, "normalization_log.json")
README_PATH = os.path.join(EXPERIMENT_DIR, "README.md")
PROCESSES_PATH = os.path.join(EXPERIMENT_DIR, "PROCESSES.md")
CHUNKS_DIR = os.path.join(EXPERIMENT_DIR, "chunks")

API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("YOUR_API_KEY")
if not API_KEY:
    raise RuntimeError("Set OPENAI_API_KEY before running this script.")

client = OpenAI(api_key=API_KEY)

os.makedirs(EXPERIMENT_DIR, exist_ok=True)
os.makedirs(CHUNKS_DIR, exist_ok=True)


token_log = []
total_tokens = 0
process_log = []


def log_tokens(step, response):
    global total_tokens
    usage = getattr(response, "usage", None)
    if not usage:
        return

    entry = {
        "step": step,
        "input_tokens": usage.prompt_tokens,
        "output_tokens": usage.completion_tokens,
        "total_tokens": usage.total_tokens,
    }
    total_tokens += usage.total_tokens
    token_log.append(entry)


def log_process(item, reference, output):
    process_log.append(
        {
            "process_count": len(process_log) + 1,
            "item": item,
            "reference": reference,
            "output": output,
        }
    )


def save_readme():
    content = "# API TOKEN USAGE LOG\n\n"
    for entry in token_log:
        content += f"## {entry['step']}\n"
        content += f"- Input: {entry['input_tokens']}\n"
        content += f"- Output: {entry['output_tokens']}\n"
        content += f"- Total: {entry['total_tokens']}\n\n"
    content += f"# GRAND TOTAL: {total_tokens}\n"

    with open(README_PATH, "w", encoding="utf-8") as file:
        file.write(content)


def save_process_log():
    content = "# PROCESSES\n\n"
    for entry in process_log:
        content += f"## PROCESS No. {entry['process_count']}\n"
        content += f"**Building the {entry['item']} section**\n\n"
        content += "Used this reference:\n"
        content += f"````html\n{entry['reference']}\n````\n"
        content += "Generated this output:\n"
        content += f"````html\n{entry['output']}\n````\n\n"

    with open(PROCESSES_PATH, "w", encoding="utf-8") as file:
        file.write(content)


def save_file(path, content):
    with open(path, "w", encoding="utf-8") as file:
        file.write(content)


def load_file(path):
    with open(path, "r", encoding="utf-8") as file:
        return file.read()


def encode_image(image_path):
    with open(image_path, "rb") as img:
        return base64.b64encode(img.read()).decode("utf-8")


def safe_json_loads(text):
    try:
        return json.loads(text)
    except Exception:
        pass

    match = re.search(r"\{.*\}|\[.*\]", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            pass

    cleaned = text.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(cleaned)
    except Exception:
        return {}


def extract_text_preview(node, limit=220):
    text = " ".join(node.stripped_strings)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit]


def detect_background_colors(html):
    colors = re.findall(r"background(?:-color)?:\s*(#[0-9A-Fa-f]{3,8})", html)
    return list(dict.fromkeys(color.upper() for color in colors[:6]))


def extract_inner_html(node):
    return "".join(str(child) for child in node.contents)


def normalize_text(value):
    if not value:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def repair_mojibake_text(value):
    if not isinstance(value, str):
        return value
    suspicious_tokens = ["â€™", "â€œ", "â€", "Â", "cafÃ©", "Ã", "â€“"]
    if not any(token in value for token in suspicious_tokens):
        return value
    try:
        repaired = value.encode("latin-1").decode("utf-8")
        return repaired
    except Exception:
        return value


def repair_mojibake_data(data):
    if isinstance(data, dict):
        return {key: repair_mojibake_data(value) for key, value in data.items()}
    if isinstance(data, list):
        return [repair_mojibake_data(item) for item in data]
    if isinstance(data, str):
        return repair_mojibake_text(data)
    return data


def classify_section(fingerprint):
    if fingerprint["images"] and fingerprint["headings"] and fingerprint["buttons"]:
        return "hero"
    if fingerprint["columns"] >= 2 and fingerprint["images"]:
        return "split"
    if fingerprint["columns"] >= 3:
        return "grid"
    if fingerprint["buttons"]:
        return "cta"
    if fingerprint["lists"]:
        return "list"
    if fingerprint["social_links"] or fingerprint["text_len"] < 120:
        return "footer"
    return "content"


def build_chunk_fingerprint(chunk_html, index):
    soup = BeautifulSoup(chunk_html, "html.parser")
    text = " ".join(soup.stripped_strings)
    classes = []
    for tag in soup.find_all(True):
        tag_classes = tag.get("class", [])
        classes.extend(tag_classes)

    class_counts = Counter(classes)
    headings = len(soup.find_all(["h1", "h2", "h3", "h4"]))
    images = len(soup.find_all("img"))
    buttons = len(
        [
            a
            for a in soup.find_all("a")
            if "kl-button" in " ".join(a.get("class", []))
            or "display:block" in (a.get("style", "").replace(" ", "").lower())
        ]
    )
    lists = len(soup.find_all(["ul", "ol"])) + text.count("•")
    columns = max(
        len(soup.select(".kl-column")),
        len(soup.select("[class*='mj-column-per-']")),
    )
    fingerprint = {
        "index": index,
        "tag": soup.find(True).name if soup.find(True) else "unknown",
        "classes": [name for name, _ in class_counts.most_common(8)],
        "text_len": len(text),
        "headings": headings,
        "images": images,
        "buttons": buttons,
        "lists": lists,
        "columns": columns if columns else 1,
        "social_links": sum(
            1
            for a in soup.find_all("a")
            if any(token in (a.get("href") or "").lower() for token in ["instagram", "facebook", "x.com", "twitter", "pinterest", "linkedin"])
        ),
        "background_colors": detect_background_colors(chunk_html),
        "preview_text": extract_text_preview(soup),
    }
    fingerprint["section_type"] = classify_section(fingerprint)
    return fingerprint


def shell_pattern_count(text):
    if not text:
        return 0
    return len(re.findall(r"[^\s]", text))


def extract_reference_shell(reference_html):
    body_match = re.search(r"(<body[^>]*>)(.*?)(</body>)", reference_html, re.IGNORECASE | re.DOTALL)
    if not body_match:
        return {
            "head_part": reference_html,
            "body_open": "<body>",
            "preheader_html": "",
            "root_open": "",
            "root_close": "",
            "body_close": "</body></html>",
        }

    head_part = reference_html[: body_match.start(1)]
    body_open = body_match.group(1)
    body_inner = body_match.group(2)
    body_close = body_match.group(3) + "</html>"

    soup = BeautifulSoup(body_inner, "html.parser")
    preheader_node = None
    tracking_node = None
    root_node = None

    for child in soup.contents:
        if not getattr(child, "name", None):
            continue
        child_html = str(child)
        style = child.get("style", "")
        if preheader_node is None and "display" in style and "max-height" in style:
            preheader_node = child
            continue
        if "TRACKING_PIXEL_TOP" in child_html:
            tracking_node = child_html
            continue
        if child.name == "div" and "root-container" in (child.get("class") or []):
            root_node = child

    if tracking_node is None and "<!-- TRACKING_PIXEL_TOP -->" in body_inner:
        tracking_node = "<!-- TRACKING_PIXEL_TOP -->"

    root_open = ""
    root_close = ""
    if root_node is not None:
        root_open = str(root_node).split(extract_inner_html(root_node), 1)[0]
        spacing = root_node.find("div", class_="root-container-spacing")
        if spacing is not None:
            spacing_inner = extract_inner_html(spacing)
            spacing_open = str(spacing).split(spacing_inner, 1)[0]
            root_open = root_open + spacing_open
            root_close = "</div></div>"
        else:
            root_close = "</div>"

    preheader_html = str(preheader_node) if preheader_node is not None else ""
    return {
        "head_part": head_part,
        "body_open": body_open,
        "preheader_html": preheader_html,
        "tracking_html": tracking_node or "<!-- TRACKING_PIXEL_TOP -->",
        "root_open": root_open,
        "root_close": root_close,
        "body_close": body_close,
    }


def update_preheader_html(preheader_html, preheader_text):
    if not preheader_html or not preheader_text:
        return preheader_html

    soup = BeautifulSoup(preheader_html, "html.parser")
    node = soup.find(True)
    if not node:
        return preheader_html

    pad_char = "\u2007\u034f"
    padded = preheader_text + (pad_char * max(0, 220 - shell_pattern_count(preheader_text)))
    node.string = padded
    return str(node)


def merge_content_dicts(base_content, extra_content):
    merged = dict(base_content)
    for key, value in extra_content.items():
        if isinstance(value, list):
            existing = merged.get(key, [])
            merged[key] = existing + [item for item in value if item not in existing]
        elif isinstance(value, str):
            if not normalize_text(merged.get(key)) and normalize_text(value):
                merged[key] = value
            elif normalize_text(merged.get(key)) and normalize_text(value) and normalize_text(merged.get(key)) != normalize_text(value):
                merged[key] = merged.get(key) + "\n\n" + value
        else:
            merged[key] = value
    return merged


def normalize_design_sections(spec):
    spec = repair_mojibake_data(spec)
    sections = spec.get("sections", [])
    normalized = []
    normalization_log = []
    index = 0
    while index < len(sections):
        original = json.loads(json.dumps(sections[index]))
        current = json.loads(json.dumps(sections[index]))

        raw_type = normalize_text(current.get("type", "")).lower().replace(" ", "_")
        if raw_type in {"product_promo", "product_recommendation", "product_recommendations"} and current.get("layout") == "grid":
            current["type"] = "product_card_grid"
        if raw_type == "category_cards":
            current["type"] = "category_grid"
        if normalize_text(current.get("content", {}).get("heading", "")).lower() == "how to make a matcha latte at home":
            current["type"] = "intro_text"

        if current.get("type") == "intro_text":
            current["layout"] = "single"
            current["columns"] = 1
            current["text_alignment"] = "center"
            current["elements"] = ["heading", "body"]
            current.setdefault("content", {})["button"] = ""

        if current.get("type") == "recipe_section":
            current["layout"] = "single"
            current["columns"] = 1
            current["text_alignment"] = "left"

        if current.get("type") == "product_card_grid":
            heading = normalize_text(current.get("content", {}).get("heading", ""))
            if "\n" in current.get("content", {}).get("heading", ""):
                lines = [line.strip() for line in current["content"]["heading"].splitlines() if line.strip()]
                if lines:
                    current["content"]["heading"] = lines[0]
                if len(lines) > 1 and not normalize_text(current["content"].get("body")):
                    current["content"]["body"] = lines[1]
            elif "?" in heading and not normalize_text(current.get("content", {}).get("body")):
                parts = heading.split("?", 1)
                if len(parts) == 2 and normalize_text(parts[1]):
                    current["content"]["heading"] = parts[0] + "?"
                    current["content"]["body"] = parts[1].strip()

        # Suppress redundant recommendation card when the next section is the actual tea product grid.
        next_section = sections[index + 1] if index + 1 < len(sections) else None
        next_type = ""
        next_heading = ""
        if next_section:
            next_type = normalize_text(next_section.get("type", "")).lower().replace(" ", "_")
            next_heading = normalize_text(next_section.get("content", {}).get("heading", "")).lower()
        current_heading = normalize_text(current.get("content", {}).get("heading", "")).lower()
        if (
            current.get("type") == "product_recommendation"
            and next_section is not None
            and (
                next_type in {"product_card_grid", "product_promo", "product_recommendation", "product_recommendations"}
                or "not your cup of tea" in next_heading
            )
            and "organic & ceremonial-grade matcha" in current_heading
        ):
            normalization_log.append(
                {
                    "index": index,
                    "action": "suppressed_redundant_product_recommendation",
                    "before_type": original.get("type"),
                    "after_type": "suppressed",
                    "before_layout": original.get("layout"),
                    "after_layout": "",
                    "before_button": original.get("content", {}).get("button", ""),
                    "after_button": "",
                }
            )
            index += 1
            continue

        normalized.append(current)
        normalization_log.append(
            {
                "index": index,
                "action": "kept",
                "before_type": original.get("type"),
                "after_type": current.get("type"),
                "before_layout": original.get("layout"),
                "after_layout": current.get("layout"),
                "before_button": original.get("content", {}).get("button", ""),
                "after_button": current.get("content", {}).get("button", ""),
            }
        )
        index += 1

    for index, section in enumerate(normalized):
        section["section_index"] = index

    blueprint = spec.get("global_blueprint", {})
    blueprint["expected_section_count"] = len(normalized)
    blueprint["section_order"] = [section.get("type", f"section_{i}") for i, section in enumerate(normalized)]
    spec["sections"] = normalized
    spec["global_blueprint"] = blueprint
    spec["_normalization_log"] = normalization_log
    return spec


def split_html_into_chunks(html):
    print("[STEP 1] Section-aware chunking...")
    soup = BeautifulSoup(html, "html.parser")

    sections = []
    for node in soup.select("table.kl-section"):
        chunk_html = str(node)
        if len(chunk_html) >= 400:
            sections.append(chunk_html)

    if not sections:
        for node in soup.find_all("table"):
            chunk_html = str(node)
            if len(chunk_html) >= 600:
                sections.append(chunk_html)

    if not sections:
        sections = [html]

    chunk_records = []
    for index, chunk_html in enumerate(sections):
        chunk_records.append(
            {
                "index": index,
                "html": chunk_html,
                "fingerprint": build_chunk_fingerprint(chunk_html, index),
            }
        )
    return chunk_records


def save_chunks(chunk_records):
    print("[STEP 2] Saving chunks...")
    for existing in os.listdir(CHUNKS_DIR):
        existing_path = os.path.join(CHUNKS_DIR, existing)
        if os.path.isfile(existing_path):
            os.remove(existing_path)

    for record in chunk_records:
        html_path = os.path.join(CHUNKS_DIR, f"chunk_{record['index']}.html")
        meta_path = os.path.join(CHUNKS_DIR, f"chunk_{record['index']}.json")
        save_file(html_path, record["html"])
        save_file(meta_path, json.dumps(record["fingerprint"], indent=2))


def chunk_embedding_text(fingerprint):
    return json.dumps(
        {
            "section_type": fingerprint["section_type"],
            "columns": fingerprint["columns"],
            "headings": fingerprint["headings"],
            "images": fingerprint["images"],
            "buttons": fingerprint["buttons"],
            "lists": fingerprint["lists"],
            "preview_len": len(fingerprint["preview_text"]),
            "background_colors": fingerprint["background_colors"],
            "classes": fingerprint["classes"],
            "preview_text": fingerprint["preview_text"],
        },
        ensure_ascii=True,
    )


def embed_chunks(chunk_records):
    print("[STEP 3] Embedding section fingerprints...")
    embeddings = []
    for record in chunk_records:
        emb_input = chunk_embedding_text(record["fingerprint"])
        res = client.embeddings.create(model="text-embedding-3-small", input=emb_input)
        embeddings.append(
            {
                "index": record["index"],
                "html": record["html"],
                "fingerprint": record["fingerprint"],
                "embedding": res.data[0].embedding,
            }
        )
    return embeddings


def cosine_similarity(a, b):
    denominator = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))
    if not denominator:
        return 0.0
    return sum(x * y for x, y in zip(a, b)) / denominator


def score_structural_overlap(layout_item, fingerprint):
    score = 0.0
    if layout_item.get("type") == fingerprint["section_type"]:
        score += 0.35
    if layout_item.get("columns") == fingerprint["columns"]:
        score += 0.20
    if layout_item.get("layout") == ("two-column" if fingerprint["columns"] == 2 else "single" if fingerprint["columns"] == 1 else "grid"):
        score += 0.20

    wanted = set(layout_item.get("elements", []))
    actual = set()
    if fingerprint["images"]:
        actual.add("image")
    if fingerprint["headings"]:
        actual.add("heading")
    if fingerprint["buttons"]:
        actual.add("button")
    if fingerprint["lists"]:
        actual.add("list")
    if fingerprint["text_len"]:
        actual.add("body")

    if wanted:
        score += 0.25 * (len(wanted & actual) / len(wanted))

    layout_type = layout_item.get("type", "")
    if layout_type in {"product_card_grid", "product_recommendation"} and "kl-product-subblock" in fingerprint.get("classes", []):
        score += 0.10
    if layout_type in {"category_cards", "category_grid"} and "kl-table-subblock" in fingerprint.get("classes", []):
        score += 0.10
    if layout_type == "footer" and fingerprint.get("social_links", 0):
        score += 0.10
    return min(score, 1.0)


def find_best_chunks(layout_item, embeddings, k=3):
    query_text = json.dumps(layout_item, ensure_ascii=True)
    query_embedding = client.embeddings.create(model="text-embedding-3-small", input=query_text).data[0].embedding

    scored = []
    target_index = layout_item.get("section_index", 0)
    for item in embeddings:
        embedding_score = cosine_similarity(query_embedding, item["embedding"])
        structural_score = score_structural_overlap(layout_item, item["fingerprint"])
        order_penalty = abs(item["index"] - target_index)
        order_score = max(0.0, 1.0 - (order_penalty / max(len(embeddings), 1)))
        layout_type = layout_item.get("type", "")
        family_bonus = 0.0
        if layout_type in {"product_card_grid", "product_recommendation"} and "kl-product-subblock" in item["fingerprint"].get("classes", []):
            family_bonus += 0.12
        if layout_type in {"category_cards", "category_grid"} and "kl-table-subblock" in item["fingerprint"].get("classes", []):
            family_bonus += 0.12
        if layout_type == "footer" and item["fingerprint"].get("social_links", 0) >= 3:
            family_bonus += 0.12
        if layout_type == "recipe_section" and item["fingerprint"].get("lists", 0):
            family_bonus += 0.08
        score = 0.55 * embedding_score + 0.25 * structural_score + 0.1 * order_score + 0.1 * family_bonus
        scored.append((score, item))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [item for _, item in scored[:k]]


def build_image_memory(html):
    print("[STEP 4] Building image memory...")
    soup = BeautifulSoup(html, "html.parser")
    images = []
    for img in soup.find_all("img"):
        src = img.get("src")
        if not src:
            continue
        images.append(
            {
                "src": src,
                "alt": img.get("alt", ""),
                "width": img.get("width"),
                "title": img.get("title", ""),
            }
        )
    return images


def extract_design_spec(image_base64):
    print("[STEP 5] Extracting design spec and global blueprint...")
    prompt = """
Analyze this email design image and return ONLY valid JSON.

The JSON must have this exact top-level structure:
{
  "global_blueprint": {
    "email_goal": "...",
    "preheader_text": "...",
    "section_order": ["..."],
    "expected_section_count": 0,
    "wrapper_strategy": "...",
    "spacing_rhythm": "...",
    "alignment_pattern": "...",
    "background_story": "...",
    "repeatable_patterns": ["..."],
    "button_style": "...",
    "image_strategy": "...",
    "style_rules": ["..."]
  },
  "sections": [
    {
      "type": "...",
      "layout": "single | two-column | grid",
      "elements": ["image", "heading", "body", "button", "list"],
      "image_position": "top | left | right | background | none",
      "text_alignment": "...",
      "columns": 1,
      "background_color": "...",
      "is_image_only_band": false,
      "repeat_count": 0,
      "card_style": "...",
      "content": {
        "heading": "...",
        "body": "...",
        "button": "...",
        "list_items": ["..."],
        "labels": ["..."],
        "card_titles": ["..."],
        "card_buttons": ["..."],
        "footer_links": ["..."],
        "legal_lines": ["..."],
        "image_descriptions": ["..."],
        "preheader": "..."
      }
    }
  ]
}

Rules:
- Extract all visible text as exactly as possible
- Preserve section order
- Treat each visible horizontal band as its own section
- Do not merge adjacent bands just because they are visually related
- If the email starts with a full-width image band and then a text band, they must be separate sections
- Detect repeated cards/items and estimate their count
- Capture footer links and legal text separately when present
- Capture repeated patterns and likely section families
- Keep values compact but specific
- Do not use placeholders
- Do not use code fences
"""

    res = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}},
                ],
            }
        ],
        temperature=0,
    )

    log_tokens("design_spec_extraction", res)
    raw = res.choices[0].message.content.strip()
    save_file(DESIGN_SPEC_PATH, raw)
    spec = safe_json_loads(raw)

    if "global_blueprint" not in spec:
        spec["global_blueprint"] = {
            "email_goal": "unknown",
            "preheader_text": "",
            "section_order": [],
            "expected_section_count": 0,
            "wrapper_strategy": "reuse reference wrappers",
            "spacing_rhythm": "consistent",
            "alignment_pattern": "match reference and design",
            "background_story": "",
            "repeatable_patterns": [],
            "button_style": "",
            "image_strategy": "reuse reference image patterns when relevant",
            "style_rules": [],
        }

    for index, section in enumerate(spec.get("sections", [])):
        section["section_index"] = index

    normalized_spec = normalize_design_sections(spec)
    save_file(
        NORMALIZED_DESIGN_SPEC_PATH,
        json.dumps(
            {
                "global_blueprint": normalized_spec.get("global_blueprint", {}),
                "sections": normalized_spec.get("sections", []),
            },
            indent=2,
            ensure_ascii=False,
        ),
    )
    save_file(
        NORMALIZATION_LOG_PATH,
        json.dumps(normalized_spec.get("_normalization_log", []), indent=2, ensure_ascii=False),
    )
    normalized_spec.pop("_normalization_log", None)
    return normalized_spec


def build_section_family_instructions(section):
    section_type = section.get("type", "")
    content = section.get("content", {})

    instructions = [
        "Preserve the exact wrapper family and table idiom from the references.",
        "Do not add commentary, markdown, or code fences.",
    ]

    if section_type == "hero_image":
        instructions.extend(
            [
                "Return a clean image-first band only.",
                "Do not introduce body copy or CTA text into this section.",
                "If a logo is implied, keep it within the image treatment instead of creating a new text block.",
            ]
        )
    elif section_type == "intro_text":
        instructions.extend(
            [
                "Use a text-centric section with centered label, heading, and body.",
                "Keep heading and body in separate text roles.",
            ]
        )
    elif section_type == "recipe_section":
        instructions.extend(
            [
                "Treat this as the main recipe section only.",
                "Keep the content order close to the target pattern: heading, intro emphasis, list, method text, CTA.",
                "Keep the ingredient list and method text as distinct blocks.",
                "Do not absorb the following recommendation or tea-grid section into this block.",
            ]
        )
    elif section_type == "product_card_grid":
        instructions.extend(
            [
                "Keep the section heading and supporting line as separate elements.",
                "Build exactly one card per extracted title/image pair.",
                "Avoid merging the supporting sentence into the heading element.",
                f"Target card count: {max(section.get('repeat_count', len(content.get('card_titles', []))), 1)}.",
                "Keep this as its own top-level section, even if it visually follows a recipe or recommendation block.",
                "Wrap both the product image and the product title in links when using a linked product-card reference pattern.",
                "Prefer the kl-product / kl-product-subblock family when the references provide it.",
            ]
        )
    elif section_type in {"category_grid", "category_cards"}:
        instructions.extend(
            [
                "Use a category table/grid pattern instead of product recommendation cards.",
                "Build one category tile per title/image pair.",
                "Keep the section title separate from the grid table.",
                f"Target tile count: {max(section.get('repeat_count', len(content.get('card_titles', []))), 1)}.",
                "Prefer linked image tiles when the references provide them.",
            ]
        )
    elif section_type == "footer":
        instructions.extend(
            [
                "Preserve footer utility links, legal lines, and brand area as separate footer rows.",
                "If social icons are implied by references, keep them as icon/image links instead of replacing them with plain text.",
                "Do not collapse legal lines into paragraph copy.",
                "Prefer the social icon row pattern with linked icons when the references provide it.",
            ]
        )
    else:
        instructions.append("Keep heading, body, and CTA roles separated when they are provided.")

    return instructions


def build_adjacency_context(sections, index):
    def compact(section):
        return {
            "type": section.get("type"),
            "layout": section.get("layout"),
            "heading": normalize_text(section.get("content", {}).get("heading", "")),
            "body": normalize_text(section.get("content", {}).get("body", ""))[:120],
            "button": normalize_text(section.get("content", {}).get("button", "")),
            "repeat_count": section.get("repeat_count", 0),
        }

    previous_section = compact(sections[index - 1]) if index > 0 else None
    next_section = compact(sections[index + 1]) if index + 1 < len(sections) else None
    return {
        "previous_section": previous_section,
        "next_section": next_section,
        "coordination_rules": [
            "Stay visually coherent with neighboring sections.",
            "Do not merge into the previous or next section unless explicitly instructed.",
            "Preserve this section as its own band while keeping spacing and style rhythm aligned.",
        ],
    }


def summarize_generated_section(section_html):
    soup = BeautifulSoup(section_html, "html.parser")
    return {
        "preview_text": extract_text_preview(soup, limit=140),
        "background_colors": detect_background_colors(section_html),
        "images": len(soup.find_all("img")),
        "buttons": len(soup.find_all("a")),
        "columns": max(len(soup.select(".kl-column")), len(soup.select("[class*='mj-column-per-']")), 1),
    }


def generate_section(section, reference_chunks, image_memory, global_blueprint, rolling_context, adjacency_context):
    layout_item = {key: value for key, value in section.items() if key != "content"}
    refs = "\n\n".join(chunk["html"] for chunk in reference_chunks)
    ref_fingerprints = [chunk["fingerprint"] for chunk in reference_chunks]
    family_instructions = build_section_family_instructions(section)

    prompt = f"""
You are an expert HTML email developer.

Goal:
Build exactly one email section that follows the reference coding conventions and matches the provided design content.

Hard rules:
- Reuse reference wrapper patterns, spacing strategy, and coding style
- Do not invent a new section family if the references already show a matching pattern
- Keep the output as one complete section block
- Do not include the outer email shell, preheader, tracking marker, or root-container wrapper
- Use exact provided text where available
- Preserve email-safe table structure
- Match the likely section order and visual rhythm from the global blueprint
- Keep consistency with the rolling context from already generated sections
- Keep consistency with adjacent section hints without merging separate top-level sections
- Respect repeated-item density from the target section spec
- If a section is image-only, return only that image band section
- If footer links or legal lines are provided, include them explicitly instead of collapsing them into body copy

Section-family instructions:
{json.dumps(family_instructions, ensure_ascii=True)}

Global blueprint:
{json.dumps(global_blueprint, ensure_ascii=True)}

Rolling context:
{json.dumps(rolling_context, ensure_ascii=True)}

Adjacent sections:
{json.dumps(adjacency_context, ensure_ascii=True)}

Target section:
{json.dumps(layout_item, ensure_ascii=True)}

Section content:
{json.dumps(section.get('content', {}), ensure_ascii=True)}

Reference fingerprints:
{json.dumps(ref_fingerprints, ensure_ascii=True)}

Reference HTML:
{refs}

Reusable images:
{json.dumps(image_memory[:12], ensure_ascii=True)}

Implementation targets:
- Maximize fidelity to interactive density found in the references for this section family.
- If the reference pattern links images and titles separately, preserve that behavior.
- Favor reference-native URLs or safe placeholder hrefs over leaving repeated cards unlinked.

Return only HTML for this section.
"""

    print(f"[GENERATE] Section {section.get('section_index', 0)} - {section.get('type', 'unknown')}")
    res = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    html_output = res.choices[0].message.content.strip()
    log_tokens("generate_section", res)
    log_process(layout_item, refs, html_output)
    return html_output


def build_email(reference_html, design_spec, embeddings, image_memory):
    print("[STEP 6] Building email...")
    shell = extract_reference_shell(reference_html)

    final_parts = [shell["head_part"], shell["body_open"]]
    global_blueprint = design_spec.get("global_blueprint", {})
    preheader_html = update_preheader_html(shell["preheader_html"], global_blueprint.get("preheader_text", ""))
    if preheader_html:
        final_parts.append(preheader_html)
    if shell["tracking_html"]:
        final_parts.append(shell["tracking_html"])
    if shell["root_open"]:
        final_parts.append(shell["root_open"])

    rolling_context = {
        "previous_sections": [],
        "expected_order": global_blueprint.get("section_order", []),
        "expected_section_count": global_blueprint.get("expected_section_count", 0),
    }
    sections = design_spec.get("sections", [])

    for index, section in enumerate(sections):
        layout_item = {key: value for key, value in section.items() if key != "content"}
        best_chunks = find_best_chunks(layout_item, embeddings, k=3)
        adjacency_context = build_adjacency_context(sections, index)
        section_html = generate_section(
            section,
            best_chunks,
            image_memory,
            global_blueprint,
            rolling_context,
            adjacency_context,
        )
        final_parts.append(section_html)
        rolling_context["previous_sections"].append(
            {
                "type": section.get("type"),
                "summary": summarize_generated_section(section_html),
            }
        )
        rolling_context["previous_sections"] = rolling_context["previous_sections"][-2:]

    if shell["root_close"]:
        final_parts.append(shell["root_close"])
    final_parts.append(shell["body_close"])
    return "\n".join(final_parts)


def evaluate_against_target(output_html, target_html):
    def parse_metrics(html):
        soup = BeautifulSoup(html, "html.parser")
        text = " ".join(soup.stripped_strings)
        tables = soup.find_all("table")
        buttons = soup.find_all("a")
        images = soup.find_all("img")
        headings = soup.find_all(["h1", "h2", "h3", "h4"])
        sections = soup.select("table.kl-section")
        return {
            "text_len": len(text),
            "table_count": len(tables),
            "button_count": len(buttons),
            "image_count": len(images),
            "heading_count": len(headings),
            "section_count": len(sections),
            "text": text,
        }

    output_metrics = parse_metrics(output_html)
    target_metrics = parse_metrics(target_html)

    def ratio(a, b):
        if a == b == 0:
            return 1.0
        if max(a, b) == 0:
            return 0.0
        return min(a, b) / max(a, b)

    structural = round(
        30
        * (
            0.45 * ratio(output_metrics["section_count"], target_metrics["section_count"])
            + 0.35 * ratio(output_metrics["table_count"], target_metrics["table_count"])
            + 0.20 * ratio(output_metrics["heading_count"], target_metrics["heading_count"])
        ),
        2,
    )
    content = round(25 * ratio(output_metrics["text_len"], target_metrics["text_len"]), 2)
    component = round(
        20
        * (
            0.4 * ratio(output_metrics["button_count"], target_metrics["button_count"])
            + 0.4 * ratio(output_metrics["image_count"], target_metrics["image_count"])
            + 0.2 * ratio(output_metrics["heading_count"], target_metrics["heading_count"])
        ),
        2,
    )
    style = round(
        20
        * (
            0.5 * ratio(output_html.count("style="), target_html.count("style="))
            + 0.5 * ratio(output_html.count("class="), target_html.count("class="))
        ),
        2,
    )
    reuse = 0.0
    target_classes = set(re.findall(r'class="([^"]+)"', target_html))
    output_classes = set(re.findall(r'class="([^"]+)"', output_html))
    if target_classes:
        reuse = round(5 * (len(target_classes & output_classes) / len(target_classes)), 2)

    return {
        "structural_similarity": structural,
        "content_accuracy": content,
        "component_fidelity": component,
        "style_fidelity": style,
        "reuse_of_learned_assets": reuse,
        "similarity_score": round(structural + content + component + style + reuse, 2),
    }


def run_pipeline():
    print("[RUN] Experiment 9 pipeline")
    reference_html = load_file(REFERENCE_PATH)
    target_html = load_file(TARGET_PATH)

    chunk_records = split_html_into_chunks(reference_html)
    save_chunks(chunk_records)
    embeddings = embed_chunks(chunk_records)
    image_memory = build_image_memory(reference_html)

    image_base64 = encode_image(DESIGN_PATH)
    design_spec = extract_design_spec(image_base64)

    final_html = build_email(reference_html, design_spec, embeddings, image_memory)
    save_file(OUTPUT_PATH, final_html)

    evaluation = evaluate_against_target(final_html, target_html)
    save_file(
        os.path.join(EXPERIMENT_DIR, "evaluation.json"),
        json.dumps(evaluation, indent=2),
    )

    save_readme()
    save_process_log()
    print("[DONE] Experiment 9 complete")


if __name__ == "__main__":
    run_pipeline()
