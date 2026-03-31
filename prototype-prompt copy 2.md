You are Codex acting as a senior staff engineer and tech lead. You will be taking the role of a senior full-stack engineer, AI systems architect, and product designer, with extensive HTML email development experience. Your task is to build a locally run HTML Email assistant tool that will be used by email developers to generate HTML emails from designs, following the developer's coding style.

# Core goals
- The tool should first take the a sample of the developer's email code and parse it to learn their coding style, and analyse the structure, patterns, and conventions used in the code.
- The generated HTML must follow the developer's coding style, including indentation, naming conventions, structure, and formatting. A third-party should not be able to distinguish between the generated code and the developer's code if the developer coded the same email.
- You will run for hours: plan first, then implement milestone by milestone. Do not skip the planning phase.




# HARD REQUIREMENTS

- Must run **locally with one command**
- Must be **production-grade**, not a prototype
- The tools should be able to run locally and be production ready.
- UI must be minimalistic and feel like a developer tool, not a consumer product.
- Scalable, Maintainable, Testable and reusable codebase
- Mono-repo with the following tech stack:
  - Frontend: Next.js, TypeScript, [Material-UI](https://github.com/mui/material-ui/tree/v7.3.9/docs/data/material/getting-started/templates/crud-dashboard)
  - Backend: Python, FastAPI
  - AI Integration: OpenAI API(with setx OPENAI_API_KEY already in place)
  - Monaco editor with prettier for editing and previewing the generated HTML code.
  - Any other necessary libraries or tools to achieve the goals, should be runnable locally.
- The generation algorithm should be near-deterministic, relying on AI only when the parts of the design to be generated were not learned from the developer's code. Given the same design, it should produce the same output consistently.
- Use **https://placehold.co (PNG format)** only when Images/icons were not learned from training data. Placeholder must:
  - Match correct dimensions
  - Preserve layout integrity
  


---

# PRODUCT FEATURES (BUILD THESE)

## Page 1: Email Workspace

- Dropzone to upload HTML samples for training
- Dropzone to upload design reference
- Generate HTML from design

---

## Page 2: Code Editor & Preview

- Syntax-highlighted HTML editor with copy html button
- side-by-side Live preview sync
- Developer-style formatting preserved



---

# ENGINEERING REQUIREMENTS

- Strong TypeScript types
- Deterministic/Near deterministic generation
- Modular architecture:
  - parser
  - generator
  - editor and preview

---

# PROCESS REQUIREMENTS (FOLLOW STRICTLY)

## 1. PLANNING FIRST

Create a `plans.md` file BEFORE coding.

It MUST include:

### A. Milestone Plan (MINIMUM 10 milestones)
Each milestone must include:
- Scope
- Key modules/files
- Acceptance criteria
- Verification steps

### B. Architecture Overview
Describe:
- Input and Parsing systems
- Deterministic/AI generation pipeline (RAG)
- Rendering system


---

## 2. SCAFFOLD SECOND

- Setup frontend + backend
- Setup vector DB
- Setup local environment
- Ensure single command runs everything

---

## 3. IMPLEMENT THIRD

- One milestone at a time
- After each:
  - Run tests
  - Validate outputs
  - Keep commits clean

---

## DELIVERABLE

A complete repo containing:
- Fully working web app
- Demo-ready default project
- `plans.md`
- Architecture documentation
- Scripts:
  - dev
  - build
  - test
  - lint
  - export

---

## RULES

- Do NOT skip planning
- Do NOT jump to implementation early
- Do NOT give vague answers
- Always justify decisions
- Always think in systems

---

## START

First:
Create `plans.md` with:
- Full milestone plan
- Architecture overview
- Risk register

Do NOT start coding until this is complete and coherent.