

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

