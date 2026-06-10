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




def run_pipeline():
    """Run the full experimental pipeline and persist every required artifact."""
    print("[RUN] Experiment 2 pipeline")
    reference_html = load_file(REFERENCE_PATH)
    target_html = load_file(TARGET_PATH)

    chunk_records = split_html_into_chunks(reference_html)
    save_chunks(chunk_records)

    print("[DONE] Experiment 2 complete")


if __name__ == "__main__":
    run_pipeline()
