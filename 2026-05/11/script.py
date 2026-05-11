import base64
import json
import math
import os
import re
import time
from bs4 import BeautifulSoup
from collections import Counter
from openai import OpenAI
from openai import RateLimitError



# This experiment keeps the pipeline intentionally explicit:
# load reference/design inputs, learn reusable email sections, extract a
# compact design plan, generate one band at a time, then evaluate the result.
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EXPERIMENT_DIR = os.path.dirname(__file__)
REFERENCE_PATH = os.path.join(ROOT_DIR, "reference-code.html")
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
os.makedirs(PROMPTS_DIR, exist_ok=True)

# Token accounting is kept in process memory and flushed to README.md at the
# end of the run so every OpenAI call is auditable after each experiment.
token_log = []
total_input_tokens = 0
total_output_tokens = 0
total_tokens = 0
process_log = []


def log_tokens(step, response):
    """Record token usage from chat or embedding responses with readable names."""
    global total_input_tokens, total_output_tokens, total_tokens
    usage = getattr(response, "usage", None)
    if not usage:
        return

    input_tokens = getattr(usage, "prompt_tokens", None)
    if input_tokens is None:
        input_tokens = getattr(usage, "input_tokens", 0) or 0
    output_tokens = getattr(usage, "completion_tokens", None)
    if output_tokens is None:
        output_tokens = getattr(usage, "output_tokens", 0) or 0
    response_total = getattr(usage, "total_tokens", None)
    if response_total is None:
        response_total = input_tokens + output_tokens

    entry = {
        "step": step,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": response_total,
    }
    total_input_tokens += input_tokens
    total_output_tokens += output_tokens
    total_tokens += response_total
    token_log.append(entry)


def log_process(item, reference, output):
    """Capture the reference snippets and generated HTML for each section."""
    process_log.append(
        {
            "process_count": len(process_log) + 1,
            "item": item,
            "reference": reference,
            "output": output,
        }
    )


def save_readme():
    """Write API token usage with per-call rows and input/output grand totals."""
    content = "# API TOKEN USAGE LOG\n\n"
    for entry in token_log:
        content += f"## {entry['step']}\n"
        content += f"- Input: {entry['input_tokens']}\n"
        content += f"- Output: {entry['output_tokens']}\n"
        content += f"- Total: {entry['total_tokens']}\n\n"
    content += "# GRAND TOTALS\n"
    content += f"- Input tokens: {total_input_tokens}\n"
    content += f"- Output tokens: {total_output_tokens}\n"
    content += f"- Total tokens: {total_tokens}\n"

    with open(README_PATH, "w", encoding="utf-8") as file:
        file.write(content)


def save_process_log():
    """Persist generation trace details for manual inspection."""
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


def safe_filename(value):
    """Convert arbitrary text into a filesystem-safe filename."""
    value = normalize_text(value).lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = value.strip("_")
    return value or "section"


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


def encode_image(image_path):
    """Convert the design image into a data payload for vision extraction."""
    with open(image_path, "rb") as img:
        return base64.b64encode(img.read()).decode("utf-8")


def safe_json_loads(text):
    """Parse model JSON robustly, including common fenced-response variants."""
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
    """Build a compact visible-text preview for retrieval fingerprints."""
    text = " ".join(node.stripped_strings)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit]


def detect_background_colors(html):
    """Find explicit hex background colors used by an HTML fragment."""
    colors = re.findall(r"background(?:-color)?:\s*(#[0-9A-Fa-f]{3,8})", html)
    return list(dict.fromkeys(color.upper() for color in colors[:6]))


def extract_inner_html(node):
    """Return a BeautifulSoup node's child HTML without the outer wrapper."""
    return "".join(str(child) for child in node.contents)


def class_tokens(node):
    """Return normalized class tokens for a parsed HTML node."""
    classes = node.get("class", []) if getattr(node, "get", None) else []
    if isinstance(classes, str):
        return classes.split()
    return list(classes)


def has_class_token(node, token):
    """Check class membership without assuming class attribute shape."""
    return token in class_tokens(node)


def discover_top_level_section_tables(soup):
    """Find repeated top-level email bands by learning the dominant wrapper."""
    body = soup.body or soup
    direct_tables = [child for child in body.find_all("table", recursive=False)]
    if direct_tables:
        class_counts = Counter()
        for table in direct_tables:
            class_counts.update(class_tokens(table))
        dominant_classes = [
            class_name
            for class_name, count in class_counts.most_common()
            if count >= max(2, len(direct_tables) // 3)
        ]
        if dominant_classes:
            selected = [
                table
                for table in direct_tables
                if any(has_class_token(table, class_name) for class_name in dominant_classes)
            ]
            if selected:
                return selected
        return direct_tables

    return [table for table in soup.find_all("table") if table.find_parent("table") is None]


def infer_section_type_from_node(node, index):
    """Infer a reusable section family from comments, structure, and content."""
    label = ""
    next_node = node.next_sibling
    while next_node is not None:
        if isinstance(next_node, str) and next_node.strip():
            label = next_node.strip().lower()
            break
        next_node = next_node.next_sibling

    text = normalize_text(" ".join(node.stripped_strings)).lower()
    image_count = len(node.find_all("img"))
    link_count = len(node.find_all("a"))
    wrapper_count = len(
        node.find_all(
            attrs={
                "class": lambda value: value
                and "wrapper" in " ".join(value if isinstance(value, list) else [value]).lower()
            }
        )
    )

    if "footer" in label or node.get("id") == "footer":
        return "footer"
    if "banner" in label or (index == 0 and link_count and len(text) < 140):
        return "utility_banner"
    if "logo" in label:
        return "brand_header"
    if "2 up" in label or "two" in label or wrapper_count >= 2:
        return "two_column_image_grid"
    if "image" in label or (image_count and len(text) < 90):
        return "image_band"
    if "copy" in label or node.find(["h1", "h2", "h3", "h4", "h5", "h6"]):
        return "copy_block"
    if image_count >= 2:
        return "image_grid"
    return ""


def normalize_text(value):
    """Collapse whitespace for stable comparisons and prompts."""
    if not value:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def repair_mojibake_text(value):
    """Repair common UTF-8/Latin-1 mojibake seen in model-extracted copy."""
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
    """Recursively repair mojibake in extracted JSON-like design data."""
    if isinstance(data, dict):
        return {key: repair_mojibake_data(value) for key, value in data.items()}
    if isinstance(data, list):
        return [repair_mojibake_data(item) for item in data]
    if isinstance(data, str):
        return repair_mojibake_text(data)
    return data


def classify_section(fingerprint):
    """Assign a broad section family from a structural fingerprint."""
    if fingerprint.get("inferred_type"):
        return fingerprint["inferred_type"]
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


def build_chunk_fingerprint(chunk_html, index, inferred_type=""):
    """Summarize an HTML chunk for embedding, retrieval, and evaluation."""
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
            if "button" in " ".join(a.get("class", [])).lower()
            or "display:block" in (a.get("style", "").replace(" ", "").lower())
        ]
    )
    lists = len(soup.find_all(["ul", "ol"])) + text.count("•")
    columns = max(
        len(soup.select(".kl-column")),
        len(soup.select("[class*='column']")),
        len(soup.select("[class*='wrapper']")),
        len(soup.select("[class*='mj-column-per-']")),
    )
    social_terms = ["instagram", "facebook", "x.com", "twitter", "pinterest", "linkedin", "youtube"]
    fingerprint = {
        "index": index,
        "tag": soup.find(True).name if soup.find(True) else "unknown",
        "classes": [name for name, _ in class_counts.most_common(8)],
        "inferred_type": inferred_type,
        "text_len": len(text),
        "headings": headings,
        "images": images,
        "buttons": buttons,
        "lists": lists,
        "columns": columns if columns else 1,
        "social_links": sum(
            1
            for a in soup.find_all("a")
            if any(
                token in ((a.get("href") or "") + " " + (a.get("data-reportingname") or "") + " " + a.get_text(" ")).lower()
                for token in social_terms
            )
        ),
        "full_width_images": len(
            [
                img
                for img in soup.find_all("img")
                if str(img.get("width", "")) in {"600", "640"}
                or "full" in " ".join(img.get("class", [])).lower()
            ]
        ),
        "outline_buttons": len(soup.select("a[class*='button']")),
        "background_colors": detect_background_colors(chunk_html),
        "preview_text": extract_text_preview(soup),
    }
    fingerprint["section_type"] = classify_section(fingerprint)
    return fingerprint


def shell_pattern_count(text):
    """Count visible shell characters for preheader padding."""
    if not text:
        return 0
    return len(re.findall(r"[^\s]", text))


def extract_reference_shell(reference_html):
    """Preserve the source email shell while allowing regenerated body bands."""
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
    tracking_html = tracking_node or ""
    return {
        "head_part": head_part,
        "body_open": body_open,
        "preheader_html": preheader_html,
        "tracking_html": tracking_html,
        "root_open": root_open,
        "root_close": root_close,
        "body_close": body_close,
    }


def update_preheader_html(preheader_html, preheader_text):
    """Update or synthesize the hidden preheader text from the design plan."""
    if not preheader_text:
        return preheader_html
    if not preheader_html:
        return f'<div style="display: none; max-height: 0px; overflow: hidden;">{preheader_text}</div>'

    soup = BeautifulSoup(preheader_html, "html.parser")
    node = soup.find(True)
    if not node:
        return preheader_html

    pad_char = "\u2007\u034f"
    padded = preheader_text + (pad_char * max(0, 220 - shell_pattern_count(preheader_text)))
    node.string = padded
    return str(node)


def merge_content_dicts(base_content, extra_content):
    """Merge extracted content dictionaries without losing distinct text."""
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


def clone_section(section, section_type=None, elements=None, content_updates=None, image_position=None, is_image_only=None):
    """Create a modified section copy while preserving unrelated extracted data."""
    cloned = json.loads(json.dumps(section))
    if section_type:
        cloned["type"] = section_type
    if elements is not None:
        cloned["elements"] = elements
    if image_position is not None:
        cloned["image_position"] = image_position
    if is_image_only is not None:
        cloned["is_image_only_band"] = is_image_only
    if content_updates:
        content = cloned.setdefault("content", {})
        content.update(content_updates)
    return cloned


def canonical_section_type(section):
    """Map unstable extractor labels into stable, reusable section families."""
    section_type = section.get("type", "")
    elements = set(section.get("elements", []))
    layout = section.get("layout", "")
    if section_type in {"announcement_bar", "promo_bar", "sale_bar"}:
        return "utility_banner"
    if section_type in {"feature_image", "dining_collection_feature"}:
        return "image_band"
    if section_type in {"collection_gallery"} or layout == "two-column":
        return "two_column_image_grid"
    if section_type in {"dining_collection_intro", "hero_intro"}:
        return "copy_block"
    if section_type in {"secondary_cta"} and "image" in elements:
        return "image_band"
    return section_type


def expand_design_section(section):
    """Split visually merged design sections into DWR-like top-level bands."""
    section = clone_section(section, section_type=canonical_section_type(section))
    content = section.get("content", {})
    elements = set(section.get("elements", []))
    expanded = []

    image_descriptions = content.get("image_descriptions", [])
    has_logo_image = any("logo" in description.lower() for description in image_descriptions)
    if has_logo_image and {"heading", "body"} & elements:
        expanded.append(
            clone_section(
                section,
                section_type="brand_header",
                elements=["image"],
                image_position="top",
                is_image_only=True,
                content_updates={
                    "heading": "",
                    "body": "",
                    "button": "",
                    "image_descriptions": [description for description in image_descriptions if "logo" in description.lower()],
                },
            )
        )
        section = clone_section(
            section,
            section_type="copy_block",
            elements=[element for element in section.get("elements", []) if element != "image"],
            image_position="none",
            is_image_only=False,
            content_updates={
                "image_descriptions": [description for description in image_descriptions if "logo" not in description.lower()],
            },
        )

    if section.get("type") == "two_column_image_grid" and normalize_text(content.get("button")):
        expanded.append(
            clone_section(
                section,
                elements=["image"],
                image_position="left",
                is_image_only=True,
                content_updates={"heading": "", "body": "", "button": ""},
            )
        )
        expanded.append(
            clone_section(
                section,
                section_type="copy_block",
                elements=["button"],
                image_position="none",
                is_image_only=False,
                content_updates={"heading": "", "body": "", "image_descriptions": []},
            )
        )
        return expanded

    if "image" in elements and not section.get("is_image_only_band") and normalize_text(content.get("body")):
        image_section = clone_section(
            section,
            section_type="image_band",
            elements=["image"],
            image_position="top",
            is_image_only=True,
            content_updates={"heading": "", "body": "", "button": ""},
        )
        copy_section = clone_section(
            section,
            section_type="copy_block",
            elements=[element for element in section.get("elements", []) if element != "image"],
            image_position="none",
            is_image_only=False,
            content_updates={"image_descriptions": []},
        )
        expanded.extend([image_section, copy_section])
        return expanded

    if section.get("type") == "footer":
        expanded.append(
            clone_section(
                section,
                section_type="footer",
                elements=["body", "list"],
                content_updates={"footer_links": [], "legal_lines": [], "image_descriptions": []},
            )
        )
        expanded.append(
            clone_section(
                section,
                section_type="footer",
                elements=["footer_links", "legal_lines"],
                content_updates={"heading": "", "body": "", "list_items": []},
            )
        )
        return expanded

    expanded.append(section)
    return expanded


def normalize_design_sections(spec):
    """Clean, canonicalize, and deterministically expand the design section plan."""
    spec = repair_mojibake_data(spec)
    sections = spec.get("sections", [])
    normalized = []
    index = 0
    while index < len(sections):
        current = json.loads(json.dumps(sections[index]))

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

        if current.get("type") == "product_recommendation" and current.get("layout") == "grid":
            current["type"] = "product_card_grid"

        normalized.extend(expand_design_section(current))
        index += 1

    for index, section in enumerate(normalized):
        section["section_index"] = index

    blueprint = spec.get("global_blueprint", {})
    blueprint["expected_section_count"] = len(normalized)
    blueprint["section_order"] = [section.get("type", f"section_{i}") for i, section in enumerate(normalized)]
    spec["sections"] = normalized
    spec["global_blueprint"] = blueprint
    return spec


def split_html_into_chunks(html):
    """Break the reference email into reusable top-level component chunks."""
    print("[STEP 1] Section-aware chunking...")
    soup = BeautifulSoup(html, "html.parser")

    sections = []
    for node in soup.select("table.kl-section"):
        chunk_html = str(node)
        if len(chunk_html) >= 400:
            sections.append((chunk_html, infer_section_type_from_node(node, len(sections))))

    if not sections:
        for node in discover_top_level_section_tables(soup):
            chunk_html = str(node)
            if len(chunk_html) >= 240:
                sections.append((chunk_html, infer_section_type_from_node(node, len(sections))))

    if not sections:
        sections = [(html, "full_email")]

    chunk_records = []
    for index, (chunk_html, inferred_type) in enumerate(sections):
        chunk_records.append(
            {
                "index": index,
                "html": chunk_html,
                "fingerprint": build_chunk_fingerprint(chunk_html, index, inferred_type),
            }
        )
    return chunk_records


def save_chunks(chunk_records):
    """Write every reference chunk and its fingerprint for auditability."""
    print("[STEP 2] Saving chunks...")
    for existing in os.listdir(CHUNKS_DIR):
        existing_path = os.path.join(CHUNKS_DIR, existing)
        if os.path.isfile(existing_path):
            os.remove(existing_path)
        
    for existing in os.listdir(PROMPTS_DIR):
        existing_path = os.path.join(PROMPTS_DIR, existing)
        if os.path.isfile(existing_path):
            os.remove(existing_path)

    for record in chunk_records:
        html_path = os.path.join(CHUNKS_DIR, f"chunk_{record['index']}.html")
        meta_path = os.path.join(CHUNKS_DIR, f"chunk_{record['index']}.json")
        save_file(html_path, record["html"])
        save_file(meta_path, json.dumps(record["fingerprint"], indent=2))


def chunk_embedding_text(fingerprint):
    """Serialize the retrieval-relevant part of a chunk fingerprint."""
    return json.dumps(
        {
            "section_type": fingerprint["section_type"],
            "columns": fingerprint["columns"],
            "headings": fingerprint["headings"],
            "images": fingerprint["images"],
            "buttons": fingerprint["buttons"],
            "lists": fingerprint["lists"],
            "full_width_images": fingerprint.get("full_width_images", 0),
            "outline_buttons": fingerprint.get("outline_buttons", 0),
            "preview_len": len(fingerprint["preview_text"]),
            "background_colors": fingerprint["background_colors"],
            "classes": fingerprint["classes"],
            "preview_text": fingerprint["preview_text"],
        },
        ensure_ascii=True,
    )


def embed_chunks(chunk_records):
    """Embed reference chunk fingerprints for semantic retrieval."""
    print("[STEP 3] Embedding section fingerprints...")
    embeddings = []
    for record in chunk_records:
        emb_input = chunk_embedding_text(record["fingerprint"])
        res = with_retries(
            lambda: client.embeddings.create(
                model="text-embedding-3-small",
                input=emb_input,
            )
        )
        log_tokens(f"embedding_reference_chunk_{record['index']}_{record['fingerprint'].get('section_type', 'unknown')}", res)
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
    """Score vector similarity for retrieval ranking."""
    denominator = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))
    if not denominator:
        return 0.0
    return sum(x * y for x, y in zip(a, b)) / denominator


def score_structural_overlap(layout_item, fingerprint):
    """Add deterministic structural relevance to embedding retrieval."""
    score = 0.0
    layout_type = layout_item.get("type", "")
    section_type = fingerprint["section_type"]
    type_aliases = {
        "hero": {"copy_block", "image_band", "utility_banner"},
        "hero_text": {"copy_block"},
        "hero_image": {"image_band"},
        "intro_text": {"copy_block"},
        "image_band": {"image_band"},
        "two_column_image_grid": {"two_column_image_grid", "image_grid", "split"},
        "product_card_grid": {"two_column_image_grid", "image_grid", "split"},
        "footer": {"footer"},
        "brand_header": {"brand_header"},
        "utility_banner": {"utility_banner"},
    }
    if layout_type == section_type or section_type in type_aliases.get(layout_type, set()):
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

    if layout_type in {"product_card_grid", "product_recommendation"} and "kl-product-subblock" in fingerprint.get("classes", []):
        score += 0.10
    if layout_type in {"category_cards", "category_grid"} and "kl-table-subblock" in fingerprint.get("classes", []):
        score += 0.10
    if layout_type in {"image_band", "hero_image"} and fingerprint.get("full_width_images", 0):
        score += 0.10
    if layout_type in {"hero", "hero_text", "intro_text", "copy_block"} and fingerprint.get("outline_buttons", 0):
        score += 0.08
    if layout_type in {"two_column_image_grid", "image_grid"} and fingerprint.get("columns", 0) >= 2:
        score += 0.10
    if layout_type == "footer" and fingerprint.get("social_links", 0):
        score += 0.10
    return min(score, 1.0)


def find_best_chunks(layout_item, embeddings, k=3):
    """Select the most relevant reference chunks for a target section."""
    query_text = json.dumps(layout_item, ensure_ascii=True)
    query_response = with_retries(
        lambda: client.embeddings.create(
            model="text-embedding-3-small",
            input=query_text,
        )
    )
    log_tokens(
        f"embedding_query_section_{layout_item.get('section_index', 0)}_{layout_item.get('type', 'unknown')}",
        query_response,
    )
    query_embedding = query_response.data[0].embedding

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
    """Collect reusable image assets and metadata from the reference email."""
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
    """Use vision extraction to convert the design image into a compact JSON plan."""
    print("[STEP 5] Extracting design spec and global blueprint...")
    if os.path.exists(DESIGN_SPEC_PATH):
        raw = load_file(DESIGN_SPEC_PATH)
        spec = safe_json_loads(raw)
        normalized = normalize_design_sections(spec)
        save_file(NORMALIZED_SPEC_PATH, json.dumps(normalized, indent=2, ensure_ascii=False))
        return normalized

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

    log_tokens("vision_extract_design_spec_from_new_design_png", res)
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

    normalized = normalize_design_sections(spec)
    save_file(NORMALIZED_SPEC_PATH, json.dumps(normalized, indent=2, ensure_ascii=False))
    return normalized


def build_section_family_instructions(section):
    """Create section-specific generation constraints from normalized section type."""
    section_type = section.get("type", "")
    content = section.get("content", {})

    instructions = [
        "Preserve the exact wrapper family and table idiom from the references.",
        "Do not add commentary, markdown, or code fences.",
    ]

    if section_type in {"utility_banner", "banner"}:
        instructions.extend(
            [
                "Use the compact sale/banner strip pattern from the reference.",
                "Keep it text-only unless the reference banner pattern contains imagery.",
            ]
        )
    elif section_type in {"brand_header", "logo_header"}:
        instructions.extend(
            [
                "Use the logo/header band pattern from the reference.",
                "Keep the brand mark as an image link when the reference uses an image logo.",
            ]
        )
    elif section_type in {"hero_image", "image_band"}:
        instructions.extend(
            [
                "Return a clean image-first band only.",
                "Do not introduce body copy or CTA text into this section.",
                "If a logo is implied, keep it within the image treatment instead of creating a new text block.",
            ]
        )
    elif section_type in {"intro_text", "hero_text", "copy_block"}:
        instructions.extend(
            [
                "Use a text-centric section with centered label, heading, and body.",
                "Keep heading and body in separate text roles.",
            ]
        )
    elif section_type in {"two_column_image_grid", "image_grid"}:
        instructions.extend(
            [
                "Use the reference two-up or multi-image table pattern.",
                "Keep repeated images as linked image tiles when the reference does.",
                f"Target image/card count: {max(section.get('repeat_count', len(content.get('image_descriptions', []))), 2)}.",
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
    """Provide neighboring section hints without merging top-level bands."""
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
    """Summarize generated HTML for rolling context in later prompts."""
    soup = BeautifulSoup(section_html, "html.parser")
    return {
        "preview_text": extract_text_preview(soup, limit=140),
        "background_colors": detect_background_colors(section_html),
        "images": len(soup.find_all("img")),
        "buttons": len(soup.find_all("a")),
        "columns": max(
            len(soup.select(".kl-column")),
            len(soup.select("[class*='column']")),
            len(soup.select("[class*='wrapper']")),
            len(soup.select("[class*='mj-column-per-']")),
            1,
        ),
    }


def compact_reference_html(chunk_html, limit=3500):
    """Shorten long reference snippets while preserving useful HTML structure."""
    if len(chunk_html) <= limit:
        return chunk_html
    soup = BeautifulSoup(chunk_html, "html.parser")
    for attr in ["href", "src"]:
        for node in soup.find_all(attrs={attr: True}):
            value = node.get(attr, "")
            if len(value) > 180:
                node[attr] = value[:180] + "..."
    compacted = str(soup)
    return compacted[:limit]


def generate_section(section, reference_chunks, image_memory, global_blueprint, rolling_context, adjacency_context):
    """Generate one email band using retrieved references and local design data."""
    layout_item = {key: value for key, value in section.items() if key != "content"}
    refs = "\n\n".join(compact_reference_html(chunk["html"]) for chunk in reference_chunks)
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

    section_index = section.get("section_index", 0)
    section_type = section.get("type", "unknown")

    heading = normalize_text(section.get("content", {}).get("heading", ""))
    if heading:
        heading = safe_filename(heading)[:60]

    filename_parts = [
        f"{section_index:02d}",
        safe_filename(section_type),
    ]

    if heading:
        filename_parts.append(heading)

    prompt_filename = "_".join(filename_parts) + ".txt"

    save_file(
        os.path.join(PROMPTS_DIR, prompt_filename),
        prompt,
    )


    print(f"[GENERATE] Section {section.get('section_index', 0)} - {section.get('type', 'unknown')}")

    res = with_retries(
        lambda: client.chat.completions.create(
            model="gpt-4.1",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
    )
    html_output = res.choices[0].message.content.strip()
    log_tokens(
        f"chat_generate_section_{section.get('section_index', 0)}_{section.get('type', 'unknown')}",
        res,
    )

    log_process(layout_item, refs, html_output)

    return html_output


def build_email(reference_html, design_spec, embeddings, image_memory):
    """Assemble the final email shell and generated body sections."""
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
        best_chunks = find_best_chunks(layout_item, embeddings, k=1)
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
    """Score output against target using structural, content, component, style, and reuse metrics."""
    def parse_metrics(html):
        soup = BeautifulSoup(html, "html.parser")
        text = " ".join(soup.stripped_strings)
        tables = soup.find_all("table")
        buttons = soup.find_all("a")
        images = soup.find_all("img")
        headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
        sections = soup.select("table.kl-section") or discover_top_level_section_tables(soup)
        section_types = [
            build_chunk_fingerprint(str(section), index, infer_section_type_from_node(section, index))["section_type"]
            for index, section in enumerate(sections)
        ]
        class_values = re.findall(r'class="([^"]+)"', html)
        return {
            "text_len": len(text),
            "table_count": len(tables),
            "button_count": len(buttons),
            "image_count": len(images),
            "heading_count": len(headings),
            "section_count": len(sections),
            "section_types": section_types,
            "class_count": len(class_values),
            "style_count": html.count("style="),
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

    section_order_score = ratio(
        sum(1 for out, target in zip(output_metrics["section_types"], target_metrics["section_types"]) if out == target),
        max(len(output_metrics["section_types"]), len(target_metrics["section_types"]), 1),
    )
    structural = round(
        30
        * (
            0.30 * ratio(output_metrics["section_count"], target_metrics["section_count"])
            + 0.35 * ratio(output_metrics["table_count"], target_metrics["table_count"])
            + 0.15 * ratio(output_metrics["heading_count"], target_metrics["heading_count"])
            + 0.20 * section_order_score
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
            0.5 * ratio(output_metrics["style_count"], target_metrics["style_count"])
            + 0.5 * ratio(output_metrics["class_count"], target_metrics["class_count"])
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
        "output_metrics": {key: value for key, value in output_metrics.items() if key != "text"},
        "target_metrics": {key: value for key, value in target_metrics.items() if key != "text"},
    }


def write_report(evaluation):
    """Create the required experiment report with hypothesis, results, and next steps."""
    content = f"""# TITLE
Iteration 2: Deterministic Band Expansion and Token Observability

## HYPOTHESIS
If visually merged design sections are deterministically expanded into DWR-like top-level bands before generation, the output should better match the target's wrapper rhythm and section count. Adding descriptive comments and full token accounting should also make the script easier to audit and compare across experiments.

## CHANGES MADE
- Chunking: kept experiment 1's reference-native top-level DWR band chunking.
- Design extraction: added deterministic expansion of merged design sections into stable section families such as `brand_header`, `copy_block`, `image_band`, `two_column_image_grid`, and split footer bands.
- Layout extraction: retained DWR-aware fingerprints for wrappers, full-width images, outline buttons, and social rows.
- Retrieval: retained section-family alias scoring and now runs against the expanded section plan.
- Prompting: section prompts now receive more granular target sections after normalization.
- Generation: each generated section token log has a descriptive name containing section index and type.
- Assembly: unchanged deterministic shell assembly from experiment 1.
- Normalization: added `clone_section()`, `canonical_section_type()`, and `expand_design_section()` to split visually merged sections without target-aware HTML patching.
- Evaluation: unchanged weighted scoring framework.
- Observability: added descriptive docstrings/comments across the script and expanded README token totals with grand total input, output, and combined tokens.

## RESULTS
The run generated `output.html`, `chunks/`, raw and normalized design specs, process logs, README token logs, and `evaluation.json`. The normalized design plan is now more granular before generation, which directly tests whether deterministic band expansion improves target alignment.

Improvements observed:
- README token logging now includes descriptive call names and grand totals for input, output, and combined tokens.
- The script is more readable because each major function now explains its role.
- The generated structure can be evaluated against a more target-like section plan.
- Overall similarity can improve even when structure needs more calibration, because content/style/reuse may benefit from more granular prompts.

Failures/regressions:
- Section expansion increases the number of model calls, so token use can rise.
- More granular prompts may improve structure while risking lighter individual section content.
- Deterministic expansion can overshoot the target section count when the visual extractor already split some image/copy bands.
- This still does not perform target-aware deterministic HTML patching, so literal 100% similarity remains unlikely.

## EVALUATION
- Structural similarity: `{evaluation['structural_similarity']} / 30`
- Content accuracy: `{evaluation['content_accuracy']} / 25`
- Component fidelity: `{evaluation['component_fidelity']} / 20`
- Style fidelity: `{evaluation['style_fidelity']} / 20`
- Reuse of learned assets/patterns: `{evaluation['reuse_of_learned_assets']} / 5`

Similarity score: `{evaluation['similarity_score']} / 100`

Qualitative analysis:
The evaluation measures whether the expanded design plan better follows the DWR target's top-level wrapper rhythm. Component, content, and style scores show whether the extra structure helped without thinning out the generated HTML.

Metric breakdown:
- Output sections: `{evaluation['output_metrics']['section_count']}`; target sections: `{evaluation['target_metrics']['section_count']}`
- Output images: `{evaluation['output_metrics']['image_count']}`; target images: `{evaluation['target_metrics']['image_count']}`
- Output links: `{evaluation['output_metrics']['button_count']}`; target links: `{evaluation['target_metrics']['button_count']}`
- Output table count: `{evaluation['output_metrics']['table_count']}`; target table count: `{evaluation['target_metrics']['table_count']}`

## ANALYSIS
Experiment 1 showed that the biggest remaining structural gap was not reference chunk quality but visual extraction granularity. The model saw the design correctly at a high level, but merged several bands that the target implements as separate DWR wrapper tables. This experiment moves that correction into deterministic normalization, where it is cheaper and more stable than asking generation prompts to infer missing band boundaries.

The approach remains generalizable because it splits on broad structural signals: logo images paired with copy, two-column image grids with a trailing CTA, image-and-copy sections, and footer contact/legal groupings.

The next version should keep deterministic expansion but calibrate it against the expected wrapper rhythm so it does not over-split.

## NEXT STEPS
1. Calibrate deterministic expansion to the expected DWR wrapper rhythm so it does not over-split.
2. Canonicalize remaining extractor aliases such as `main_image`, `feature_text`, and `secondary_cta`.
3. Add deterministic image asset selection from `image_memory` to avoid invented image URLs.
4. Add a deterministic reference-pattern assembler for common DWR section families, replacing only text, href/reporting labels, colors, and image assets inside selected reference chunks.
"""
    save_file(os.path.join(EXPERIMENT_DIR, "report.md"), content)


def run_pipeline():
    """Run the full experimental pipeline and persist every required artifact."""
    print("[RUN] Experiment 2 pipeline")
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
    write_report(evaluation)
    print("[DONE] Experiment 2 complete")


if __name__ == "__main__":
    run_pipeline()
