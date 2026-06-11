def infer_section_type_from_node_ai(node, index):

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

