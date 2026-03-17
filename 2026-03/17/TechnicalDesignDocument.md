<!-- The workflow details a simple web app that allows an professional HTML email developer to train an AI model on how they write email code and then generate the HTML code for a new email design -->


---

# Technical Design Document

## AI-Assisted HTML Email Code Generation System

## 1. Overview

### 1.1 Purpose

This system enables professional HTML email developers to train an AI-assisted application on their **email design system and coding style**, allowing the system to automatically generate HTML code for new email designs while maintaining the developer’s conventions, frameworks, and brand specifications.

The system uses **vector embeddings, similarity search, and iterative visual validation** to generate HTML email templates that closely match the developer’s style and the uploaded design.

### 1.2 Key Goals

- Learn and model a developer’s **email design system and coding style**
- Store **email sections and their properties as embeddings**
- Convert new **visual email designs into HTML**
- Maintain **consistency with frameworks** (MJML, Marketo, HubSpot, plain HTML, etc.)
- Provide **traceability between generated code and training sources**
- Enable **human-in-the-loop refinement**

---

# 2. System Architecture

## 2.1 High-Level Architecture

The system consists of four major subsystems:

1. **Design System Learning Module**
2. **Email Section Embedding Pipeline**
3. **Design Ingestion & Preprocessing Engine**
4. **HTML Generation & Validation Engine**

### Architecture Diagram (Conceptual)

```
                +-----------------------+
                | Email Developer       |
                | Uploads HTML Emails   |
                +----------+------------+
                           |
                           v
           +-------------------------------+
           | Design System Learning Module |
           +-------------------------------+
                           |
                           v
                 Vector Embedding Store
                 (Design System Index)
                           |
                           v
      +----------------------------------------+
      | Email Section Embedding Pipeline       |
      | - Section segmentation                 |
      | - Natural language description         |
      | - Screenshot capture                   |
      +----------------------------------------+
                           |
                           v
                Vector Database (Sections)

---------------------------------------------------------------

            New Email Design Upload (PNG/JPEG)
                           |
                           v
     +---------------------------------------------+
     | Design Ingestion & Preprocessing Engine     |
     | - Section segmentation                      |
     | - Visual feature extraction                 |
     | - Natural language description generation   |
     +---------------------------------------------+
                           |
                           v
          +-----------------------------------+
          | HTML Generation & Validation      |
          | - Similarity search               |
          | - Code generation                 |
          | - Screenshot comparison           |
          | - Iterative correction            |
          +-----------------------------------+
                           |
                           v
               Generated HTML Email Template
```

---

# 3. Core Technologies

| Layer            | Suggested Technologies            |
| ---------------- | --------------------------------- |
| Frontend         | React / Next.js                   |
| Backend          | Node.js / Python                  |
| AI Orchestration | LangChain / LlamaIndex            |
| LLM              | GPT / Claude / Open-source models |
| Vision Model     | GPT-4o Vision / similar           |
| Vector Database  | Pinecone / Weaviate / pgvector    |
| HTML Rendering   | Puppeteer / Playwright            |
| Image Processing | OpenCV                            |
| Storage          | S3 / Blob Storage                 |
| Task Queue       | Celery / Redis / BullMQ           |

---

# 4. Data Models

## 4.1 Design System Object

```
DesignSystem
{
  id: UUID
  fonts: []
  colours: []
  backgroundColours: []
  typography:
    fontSizes: []
    lineHeights: []
    letterSpacing: []
  frameworks: []
  components: []
  layoutPatterns: []
  codingConventions: text
  embedding: vector
}
```

---

## 4.2 Email Section Object

```
EmailSection
{
  uid: UUID
  screenshotPath: string
  naturalLanguageDescription: text
  htmlCode: text
  embedding: vector
  layoutType: string
  components: []
}
```

---

## 4.3 Generated Section Object

```
GeneratedSection
{
  id: UUID
  generatedHTML: text
  designReference: image
  matchedSources: [EmailSection.uid]
  similarityScores: []
  correctionHistory: []
}
```

---

# 5. System Workflows

---

# Stage 1 — Learn the Email Design System

### Objective

Extract the developer’s design system and coding conventions from existing HTML emails.

### Process

#### Step 1: HTML Analysis

The system parses the email HTML and extracts:

**Styling Properties**

- Colours
- Background colours
- Font sizes
- Line heights
- Letter spacing
- Font families
- Font import methods

**Framework Detection**

Identify frameworks such as:

- MJML
- Marketo
- HubSpot
- Plain HTML
- Custom templates

**Component Identification**

Detect reusable elements:

- Buttons
- Images
- Headings
- Paragraph blocks
- Dividers
- Containers
- Spacers

**Layout Structure**

Identify layout hierarchy:

- Rows
- Columns
- Nested blocks
- Table structures

---

#### Step 2: Draft Design System Generation

The system compiles extracted data into a **draft design system specification**.

Example output:

```
Typography
- Font: Inter (Google Fonts)
- Heading Size: 28px
- Body Size: 16px

Colours
- Primary: #0055FF
- Secondary: #F5F5F5

Components
- Primary Button
- Secondary Button
- Hero Image
- Text Block

Layout
- 600px fixed width
- Table-based layout
```

---

#### Step 3: Human Validation

The developer refines:

- Component definitions
- Syntax preferences
- Brand colour rules
- Framework-specific constraints

---

#### Step 4: Vector Embedding Storage

The finalized design system is converted to a **vector embedding** and stored in the vector database.

Purpose:

- Style-aware code generation
- Framework consistency
- Queryable style memory

---

# Stage 2 — Embed the HTML Email Sections

### Objective

Create a reusable database of email components and layouts.

---

### Step 1: Section Segmentation

Each email is divided into **logical sections** such as:

- Header
- Hero
- Content blocks
- Feature rows
- CTA blocks
- Footer

---

### Step 2: Visual Description Generation

Each section is converted into a detailed natural language description.

Example:

```
Two-column layout.
Left column contains an image.
Right column contains heading, paragraph, and primary CTA button.
Background colour is white.
Text is centered.
```

---

### Step 3: Screenshot Capture

The section is rendered and captured using:

- Puppeteer
- Playwright

Stored as an image file.

---

### Step 4: Vector Embedding Storage

Each section is stored as a vector embedding containing:

```
{
  description,
  screenshot,
  uid
}
```

Purpose:

- Visual + semantic similarity search
- Layout matching

---

# Stage 3 — New Email Design Preprocessing

### Input

User uploads a **new email design image**.

Supported formats:

- PNG
- JPEG
- Figma exports

---

### Step 1: Section Detection

The system segments the design into sections using:

- Computer vision
- Layout detection
- Vector database references

---

### Step 2: Feature Extraction

For each section:

Extract visual properties:

- Layout
- Spacing
- Alignment
- Colours
- Components

---

### Step 3: Natural Language Conversion

Example output:

```
Full-width hero banner
Large centered heading
Subtext paragraph
Primary CTA button
Background colour #F3F4F6
```

These descriptions are used for similarity retrieval.

---

# Stage 4 — HTML Code Generation

### Objective

Convert the design into HTML email code consistent with the learned design system.

---

## Step 1: Section Similarity Search

For each new section:

Query vector database:

```
Top K similar sections
```

Matching is based on:

- visual similarity
- component structure
- layout
- description

---

## Step 2: Code Generation

The system uses retrieved HTML sections as **templates**.

Generation rules:

- Maintain framework syntax
- Preserve layout structure
- Update styles to match new design
- Reuse known components

---

## Step 3: Self-Correction Loop

To ensure visual accuracy:

1. Render generated HTML
2. Take screenshot
3. Compare with design section
4. Identify discrepancies

Examples:

- padding mismatch
- font size differences
- incorrect alignment

The system iteratively corrects the HTML.

---

## Step 4: Source Mapping

Each generated section maintains traceability.

Example:

```
Generated Section: Hero

Sources:
- Section UID: 8fa23
- Section UID: a7731
```

This enables developers to trace:

- which templates influenced the generation
- where code structure originated

---

## Step 5: Template Assembly

Generated sections are combined into a final email template.

Developer UI allows:

- hover to inspect source mappings
- edit sections
- refine design system

---

# 6. Developer Interface

Features include:

### Upload

- HTML training emails
- New design images

### Design System Editor

Editable:

- colours
- components
- layout rules

### Section Inspector

Hover UI shows:

```
Generated Section
↓
Source sections used
↓
Edit original template
```

---

# 7. Key Algorithms

## 7.1 Section Similarity Retrieval

Vector search using:

```
cosine similarity
```

Input embedding:

```
[section description + visual embedding]
```

Output:

```
Top K similar sections
```

---

## 7.2 Visual Diff Algorithm

Used for self-correction loop.

Methods:

- pixel comparison
- perceptual hash
- structural similarity index (SSIM)

---

# 8. Performance Considerations

### Parallel Processing

Sections processed **independently** to:

- reduce latency
- reduce context window usage

---

### Caching

Cache frequently used components:

- buttons
- headers
- footers

---

### Embedding Optimization

Use **hybrid embeddings**:

```
visual + textual
```

---

# 9. Future Enhancements

### Multi-Developer Training

Allow multiple coding styles.

---

### Figma Integration

Direct import of:

- frames
- components

---

### Design System Versioning

Track changes across versions.

---

### Fine-Tuned Code Model

Train model on:

- MJML
- responsive email constraints
- table-based layouts

---

# 10. Success Metrics

| Metric                   | Target            |
| ------------------------ | ----------------- |
| HTML generation accuracy | >95% visual match |
| Generation time          | <30 seconds       |
| Manual corrections       | <10%              |
| Component reuse          | >70%              |
