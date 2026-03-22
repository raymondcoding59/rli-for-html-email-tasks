import os
import base64
import numpy as np
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI

# -----------------------------
# Init
# -----------------------------
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SNIPPET_DIR = os.path.join(BASE_DIR, "snippets")

# -----------------------------
# Mock "vector DB"
# -----------------------------
snippets = [
    {
        "id": "card",
        "description": "product card with image title price and button",
        "file": "card.html"
    },
    {
        "id": "hero",
        "description": "hero section with heading and call to action button",
        "file": "hero.html"
    },
    {
        "id": "header",
        "description": "website header with logo and navigation links",
        "file": "header.html"
    },
    {
        "id": "footer",
        "description": "email footer with logo, thanks, copyright and address",
        "file": "footer.html"
    }
]

# -----------------------------
# Embedding function
# -----------------------------
def embed(text: str):
    res = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return np.array(res.data[0].embedding)




def load_html(file_name: str):
    try:
        path = os.path.join(SNIPPET_DIR, file_name)
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"❌ Failed to load {file_name}:", e)
        return ""




# -----------------------------
# Precompute embeddings
# -----------------------------
print("🔄 Loading snippets + embeddings...")

for s in snippets:
    try:
        # Load HTML from file
        s["html"] = load_html(s["file"])

        # Generate embedding from description
        s["embedding"] = embed(s["description"])

    except Exception as e:
        print(f"❌ Failed for {s['id']}: {e}")

print("✅ Snippets ready")


# -----------------------------
# Debug check (TEMP)
# -----------------------------
for s in snippets:
    print(s["id"], "HTML loaded:", len(s.get("html", "")) > 0)


# -----------------------------
# Cosine similarity
# -----------------------------
def cosine(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


# -----------------------------
# Image → UI description
# -----------------------------
def describe_image(image_bytes: bytes):
    try:
        b64 = base64.b64encode(image_bytes).decode()

        res = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Describe this UI layout in terms of components and structure."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{b64}"
                            }
                        }
                    ]
                }
            ]
        )

        return res.choices[0].message.content

    except Exception as e:
        print("❌ Vision error FULL:", repr(e))
        return f"ERROR: {str(e)}"

# -----------------------------
# Retrieve similar snippets
# -----------------------------
def retrieve(query: str, k=1):
    try:
        q_emb = embed(query)

        scored = []
        for s in snippets:
            if "embedding" not in s:
                continue
            score = cosine(q_emb, s["embedding"])
            scored.append((score, s))

        scored.sort(reverse=True, key=lambda x: x[0])

        return [s for _, s in scored[:k]]

    except Exception as e:
        print("❌ Retrieval error:", e)
        return []


# -----------------------------
# Generate final HTML
# -----------------------------
def generate_html(description: str, retrieved, image_bytes: bytes):
    try:
        
        
        b64 = base64.b64encode(image_bytes).decode()

        context = "\n\n".join([
            f"Component ({r['id']}):\n{r['html']}"
            for r in retrieved
        ])

        prompt = f"""
                    You are an expert email developer.

                    Your task is to generate HTML for a new email design section while strictly following the coding style and structure of a provided reference email.

                    CRITICAL RULE:
                    The reference HTML must be treated as the BASE TEMPLATE. You are NOT allowed to rebuild the email section from scratch. You must MODIFY the reference HTML only where the design requires changes.

                    Your output must be structurally identical to the reference template unless a change is required by the design.


                    INPUTS YOU WILL RECEIVE
                    1. A REFERENCE EMAIL HTML
                    2. A DESIGN IMAGE

                    OBJECTIVE
                    Replicate the design while preserving the reference code structure exactly.

                    1. PRESERVE STRUCTURE
                    Do not change:
                    - wrapper structure
                    - section hierarchy
                    - Outlook conditional comments (if applicable)
                    - table nesting
                    - div nesting (if applicable)
                    - class names
                    - inline styles
                    - spacing utilities


                    2. DO NOT SIMPLIFY
                    Do NOT:
                    - rewrite the HTML
                    - remove wrappers
                    - collapse tables
                    - change padding systems
                    - change responsive classes
                    - refactor styles
                    - reorganize markup

                    3. MODIFY ONLY DESIGN CONTENT
                    Only change:

                    - image URLs
                    - text copy
                    - button labels
                    - links
                    - colors if the design requires
                    - sections added or removed in the design

                    4. WHEN ADDING NEW CONTENT
                    You must replicate the same structural pattern used in the reference file.

                    For example:
                    If adding a text block, copy the exact structure used for another text block in the reference.

                    Never invent new structures. Always reuse the existing patterns.

                    5. OUTPUT FORMAT
                    Return ONLY the final HTML.
                    Do not explain anything.
                    Do not summarize.
                    Do not add comments.

                    6. VALIDATION BEFORE OUTPUT
                    Before returning the result ensure:

                    - all Outlook conditional tables remain
                    - class names remain unchanged
                    - wrapper nesting depth remains the same
                    - responsive behavior is preserved

                    If the design and reference already match, return the reference HTML unchanged.


                    REFERENCE EMAIL HTML:{context}

                """

        res = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"{prompt}"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{b64}"
                            }
                        }
                    ]
                }
            ]
        )

        return res.choices[0].message.content

    except Exception as e:
        print("❌ Generation error:", e)
        return "<div>Error generating HTML</div>"


# -----------------------------
# API endpoint
# -----------------------------
@app.post("/generate")
async def generate(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()

        print("📸 Image received")

        description = describe_image(image_bytes)
        print("🧠 Description:", description)

        retrieved = retrieve(description)
        print("🔎 Retrieved:", [r["id"] for r in retrieved])

        html = generate_html(description, retrieved, image_bytes)

        return {
            "description": description,
            "html": html
        }

    except Exception as e:
        print("❌ Endpoint error:", e)
        return {
            "description": "Error",
            "html": "<div>Something went wrong</div>"
        }