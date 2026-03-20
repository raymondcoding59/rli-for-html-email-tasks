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
def retrieve(query: str, k=3):
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
def generate_html(description: str, retrieved):
    try:
        context = "\n\n".join([
            f"Component ({r['id']}):\n{r['html']}"
            for r in retrieved
        ])

        prompt = f"""
You are an expert frontend developer.

UI description:
{description}

Here are similar components:
{context}

Instructions:
- Generate clean semantic HTML
- Reuse patterns from the provided components
- Do NOT include explanations
- Do NOT include markdown
- Return ONLY HTML

Output:
"""

        res = client.chat.completions.create(
            model="gpt-4.1",
            messages=[{"role": "user", "content": prompt}]
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

        html = generate_html(description, retrieved)

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