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


def extract_text_preview(node, limit=220):
    """Build a compact visible-text preview for retrieval fingerprints."""
    text = " ".join(node.stripped_strings)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit]


def detect_background_colors(html):
    """Find explicit hex background colors used by an HTML fragment."""
    colors = re.findall(r"background(?:-color)?:\s*(#[0-9A-Fa-f]{3,8})", html)
    return list(dict.fromkeys(color.upper() for color in colors[:6]))


def infer_section_type_from_node_ai(node, index):
    """
    Use GPT to classify an email section into a reusable section family.
    Falls back to deterministic defaults if classification fails.
    """

    try:
        fingerprint = build_chunk_fingerprint(
            str(node),
            index,
            ""
        )

        prompt = f"""
Classify this email section.

Return ONLY valid JSON:

{{
  "section_type": "..."
}}

Allowed values:
- footer
- utility_banner
- brand_header
- copy_block
- image_band
- image_grid
- two_column_image_grid
- hero
- content

Section fingerprint:

{json.dumps(fingerprint, indent=2)}
"""

        response = with_retries(
            lambda: client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                response_format={"type": "json_object"},
            )
        )


        raw = response.choices[0].message.content.strip()

        try:
            result = json.loads(raw)
        except Exception:
            print(
                f"[CLASSIFY WARNING] "
                f"Chunk {index}: invalid JSON response"
            )
            return "content"

        section_type = (
            result.get("section_type", "")
            .strip()
            .lower()
        )

        allowed_types = {
            "footer",
            "utility_banner",
            "brand_header",
            "copy_block",
            "image_band",
            "image_grid",
            "two_column_image_grid",
            "hero",
            "content",
        }

        if section_type not in allowed_types:
            print(
                f"[CLASSIFY WARNING] "
                f"Chunk {index}: unknown type '{section_type}'"
            )
            return "content"

        print(
            f"[CLASSIFY] "
            f"Chunk {index} -> {section_type}"
        )

        return section_type

    except RateLimitError:
        print(
            f"[CLASSIFY ERROR] "
            f"Chunk {index}: rate limit exceeded"
        )
        return "content"

    except Exception as error:
        print(
            f"[CLASSIFY ERROR] "
            f"Chunk {index}: {error}"
        )
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
    return fingerprint


def split_html_into_chunks(html):
    """Break the reference email into reusable top-level component chunks."""
    print("Splitting reference HTML into chunks...")
    soup = BeautifulSoup(html, "html.parser")

    sections = []
    for node in soup.select("div.component-wrapper"):
        chunk_html = str(node)
        if len(chunk_html) >= 400:
            sections.append((chunk_html, infer_section_type_from_node_ai(node, len(sections))))

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
    print("Saving chunks...")
    for existing in os.listdir(CHUNKS_DIR):
        existing_path = os.path.join(CHUNKS_DIR, existing)
        if os.path.isfile(existing_path):
            os.remove(existing_path)
        

    for record in chunk_records:
        html_path = os.path.join(CHUNKS_DIR, f"chunk_{record['index']}.html")
        meta_path = os.path.join(CHUNKS_DIR, f"chunk_{record['index']}.json")
        save_file(html_path, record["html"])
        save_file(meta_path, json.dumps(record["fingerprint"], indent=2))


def run_pipeline():
    """Run the full experimental pipeline and persist every required artifact."""
    print("[START]")
    reference_html = load_file(REFERENCE_PATH)
    chunk_records = split_html_into_chunks(reference_html)
    save_chunks(chunk_records)
    print("[DONE]")


if __name__ == "__main__":
    run_pipeline()
