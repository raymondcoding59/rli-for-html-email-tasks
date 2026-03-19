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

# -----------------------------
# Load Snippets from Files
# -----------------------------
def load_snippets_from_disk(directory="snippets"):
    loaded_snippets = []
    
    # Check if directory exists to avoid crashes
    if not os.path.exists(directory):
        print(f"⚠️ Warning: Directory '{directory}' not found.")
        return loaded_snippets

    # Define descriptions (you could also store these in a JSON file later)
    descriptions = {
        "card": "product card with image title price and button",
        "hero": "hero section with heading and call to action button",
        "header": "website header with logo and navigation links"
    }

    for filename in os.listdir(directory):
        if filename.endswith(".html"):
            snippet_id = filename.replace(".html", "")
            file_path = os.path.join(directory, filename)
            
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            loaded_snippets.append({
                "id": snippet_id,
                "description": descriptions.get(snippet_id, f"UI component: {snippet_id}"),
                "html": content
            })
    
    return loaded_snippets

# Replace the hardcoded list
snippets = load_snippets_from_disk()

# -----------------------------
# Embedding function
# -----------------------------
def embed(text: str):
    # ... (remains the same as your original code)
    res = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return np.array(res.data[0].embedding)

# -----------------------------
# Precompute embeddings
# -----------------------------
print("🔄 Precomputing embeddings for loaded files...")
for s in snippets:
    try:
        s["embedding"] = embed(s["description"])
    except Exception as e:
        print(f"❌ Failed embedding for {s['id']}: {e}")

print(f"✅ {len(snippets)} snippets ready")

# ... (rest of your functions: cosine, describe_image, retrieve, generate_html, and the POST endpoint)