import os
from openai import OpenAI
from fastapi import FastAPI, UploadFile, File
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
import numpy as np
import ast
import base64

def extract_style(html_code):

    prompt = f"""
Analyze this HTML email code.

Identify the developer's coding patterns including:

- table structure
- spacing method
- font stack
- button style
- CSS strategy
- media queries
- Outlook compatibility hacks
- comment style

Return the result as JSON.

HTML:
{html_code}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content


client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)



models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/upload-sample")
async def upload_sample(file: UploadFile = File(...)):

    contents = await file.read()
    html_code = contents.decode("utf-8")

    db: Session = SessionLocal()

    # Store email sample
    sample = models.EmailSample(html_code=html_code)
    db.add(sample)
    db.commit()

    # Extract developer style
    style = extract_style(html_code)

    dev_style = models.DeveloperStyle(style_json=style)
    db.add(dev_style)
    db.commit()

    # Create embedding
    embedding = create_embedding(html_code)

    embedding_record = models.EmailEmbedding(
        embedding=str(embedding),
        html_code=html_code
    )

    db.add(embedding_record)
    db.commit()

    return {
        "message": "Sample stored, style extracted, embedding saved"
    }


    
def create_embedding(text):

    # limit size to avoid token overflow
    max_chars = 4000
    text = text[:max_chars]

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )

    return response.data[0].embedding


#This calculates vector similarity, higher score = more similar.
def cosine_similarity(vec1, vec2):

    vec1 = np.array(vec1)
    vec2 = np.array(vec2)

    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


#This function: creates embedding for input, compares with stored embeddings, returns top matches
def retrieve_similar_emails(query_text, top_k=3):

    db: Session = SessionLocal()

    # create embedding for query
    query_embedding = create_embedding(query_text)

    # get stored embeddings
    records = db.query(models.EmailEmbedding).all()

    similarities = []

    for record in records:

        stored_embedding = ast.literal_eval(record.embedding)

        score = cosine_similarity(query_embedding, stored_embedding)

        similarities.append((score, record.html_code))

    similarities.sort(reverse=True)

    return similarities[:top_k]


#Test endpoint to retrieve similar emails
@app.post("/search-emails")
async def search_emails(query: str):

    results = retrieve_similar_emails(query)

    return {
        "matches": results
    }
    

#function that analyzes the input image.
def analyze_email_design(image_bytes):

    prompt = """
Analyze this email design image.

Identify the structure of the email including:

- sections
- images
- text blocks
- buttons
- columns
- background colors
- spacing

Return the result as JSON describing the layout.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_bytes}"
                        }
                    }
                ]
            }
        ]
    )

    return response.choices[0].message.content


#image upload endpoint
@app.post("/analyze-design")
async def analyze_design(file: UploadFile = File(...)):

    contents = await file.read()

    image_base64 = base64.b64encode(contents).decode("utf-8")

    layout = analyze_email_design(image_base64)

    return {
        "layout": layout
    }
    
    
    
#Function to generate new email code based on a style description
def generate_email_html(layout_json, similar_emails):

    examples = ""

    for score, html in similar_emails:
        examples += f"\nExample Email:\n{html}\n"

    prompt = f"""
You are an expert HTML email developer.

The developer has a specific coding style.

Below are examples of how the developer writes HTML emails.

{examples}

Using that coding style, generate an HTML email based on this layout:

{layout_json}

Rules:

- Use table based layouts
- Use inline CSS
- Ensure compatibility with email clients
- Follow the coding style in the examples
- Email width should be 600px
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content



#Endpoint to generate email code based on style and layout
@app.post("/generate-email")
async def generate_email(file: UploadFile = File(...)):

    contents = await file.read()

    image_base64 = base64.b64encode(contents).decode("utf-8")

    # Step 1: Analyze design layout
    layout = analyze_email_design(image_base64)

    # Step 2: Retrieve similar emails
    similar_emails = retrieve_similar_emails(layout)

    # Step 3: Generate HTML
    html = generate_email_html(layout, similar_emails)

    return {
        "layout": layout,
        "generated_html": html
    }