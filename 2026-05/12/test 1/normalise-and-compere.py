from pathlib import Path
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
import re


BASE_DIR = Path(__file__).resolve().parent

RESULT_FILE = BASE_DIR / "result.html"
EXPECTED_FILE = BASE_DIR / "expected.html"


# Tags where whitespace matters and should be preserved
PRESERVE_WHITESPACE_TAGS = {
    "pre",
    "code",
    "textarea",
    "script",
    "style",
}


def normalize_text_content(text: str) -> str:
    """
    Collapse repeated whitespace into single spaces.
    """
    return re.sub(r"\s+", " ", text).strip()


def normalize_html(html: str) -> str:
    """
    Normalize HTML so semantically identical files become directly comparable.

    This removes discrepancies caused by:
    - extra spaces
    - tabs
    - indentation
    - blank lines
    - inconsistent attribute spacing

    Works for arbitrary HTML structures.
    """

    soup = BeautifulSoup(html, "html.parser")

    # Remove comments
    for comment in soup.find_all(string=lambda text: isinstance(text, type(soup.comment))):
        comment.extract()

    # Normalize attributes ordering and spacing
    for tag in soup.find_all(True):
        if tag.attrs:
            normalized_attrs = {}

            for key in sorted(tag.attrs.keys()):
                value = tag.attrs[key]

                # Normalize class lists and multi-value attrs
                if isinstance(value, list):
                    value = sorted(normalize_text_content(str(v)) for v in value)

                elif isinstance(value, str):
                    value = normalize_text_content(value)

                normalized_attrs[key] = value

            tag.attrs = normalized_attrs

    # Normalize text nodes except where whitespace is meaningful
    for text_node in soup.find_all(string=True):
        parent = text_node.parent.name if text_node.parent else ""

        if parent not in PRESERVE_WHITESPACE_TAGS:
            normalized = normalize_text_content(str(text_node))
            text_node.replace_with(normalized)

    # Serialize HTML in a compact canonical form
    normalized_html = str(soup)

    # Remove whitespace between tags
    normalized_html = re.sub(r">\s+<", "><", normalized_html)

    # Final whitespace cleanup
    normalized_html = re.sub(r"\s+", " ", normalized_html).strip()

    return normalized_html


def write_normalized_file(path: Path, normalized_html: str):
    """
    Overwrite the source file with normalized HTML.
    """
    with open(path, "w", encoding="utf-8") as f:
        f.write(normalized_html)


def file_similarity(file1: Path, file2: Path) -> float:
    with open(file1, "r", encoding="utf-8") as f1:
        html1 = normalize_html(f1.read())

    with open(file2, "r", encoding="utf-8") as f2:
        html2 = normalize_html(f2.read())

    # Update source files with normalized HTML
    write_normalized_file(file1, html1)
    write_normalized_file(file2, html2)

    return SequenceMatcher(None, html1, html2).ratio()


if __name__ == "__main__":
    score = file_similarity(RESULT_FILE, EXPECTED_FILE)
    print(f"Similarity: {score * 100:.2f}%")
