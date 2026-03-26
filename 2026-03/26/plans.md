# Design-to-HTML Email AI Agent Plan

## Product Intent

Build a locally runnable, production-grade AI Email Developer Agent that converts design references into production-ready HTML emails while learning and reproducing a developer's coding style. The product must be demo-polished for non-technical stakeholders and architecturally credible for engineers: deterministic outputs, strong typing, modular subsystems, reproducible workflows, and transparent verification at each milestone.

## Opinionated Product Decisions

- Frontend: Next.js App Router with TypeScript for a polished app shell, strong local DX, and easy integration of editor, preview, analytics, and inspection tooling.
- Backend: Node.js TypeScript service layer inside the same monorepo to keep single-command local startup and shared contracts simple.
- Workspace model: local project storage with explicit versioned artifacts for samples, parsed structures, embeddings, generation runs, refinement passes, and analytics snapshots.
- Vector store: local SQLite-backed store for deterministic, portable retrieval metadata and embedding persistence.
- Rendering: Chromium-based render pipeline for HTML snapshots and visual comparison because email fidelity work needs repeatable screenshots.
- Diff pipeline: hybrid scoring model combining structural HTML diff, token/style heuristics, and rendered-image comparison rather than relying on a single AI judge.
- AI architecture: deterministic retrieval-augmented generation with stable prompts, canonicalized context ordering, fixed seeds where supported, and rule-based post-processing to reduce drift.
- Editor: Monaco-based code editor for professional ergonomics and predictable HTML editing behavior.
- State/contracts: Zod + TypeScript shared schemas for all frontend/backend boundaries.

## Architecture Overview

### 1. System Topology

The system will ship as a monorepo with a single primary web application and modular backend engines:

- `apps/web`: Next.js UI and API routes for local-first orchestration.
- `packages/contracts`: shared TypeScript types and Zod schemas.
- `packages/email-core`: email parsing, normalization, structural models.
- `packages/retrieval`: snippet indexing, embeddings, similarity search.
- `packages/generator`: prompt assembly, deterministic generation orchestration, repair passes.
- `packages/diff-engine`: design diffing, style diffing, refinement scoring.
- `packages/rendering`: HTML rendering, DOM extraction, screenshot production.
- `packages/assistant`: contextual suggestions, questionnaires, preference memory.
- `packages/analytics`: time-saved estimates, historical tracking, export models.
- `packages/ui`: reusable design system and shared UI components.

### 2. Email Structure Model

The canonical email model is the backbone of determinism and diffing. Raw uploaded HTML will be transformed into:

- Document metadata
- Table/layout tree
- Component blocks
- Inline style maps
- Asset references
- Typography tokens
- Spacing tokens
- Reusable snippet signatures

This normalized representation allows:

- Style learning independent of raw formatting noise
- Better retrieval of structurally similar examples
- Rule-based validation before generation
- Deterministic serialization back to HTML

### 3. Parsing System

The parsing system will ingest developer-provided HTML samples and produce both raw and normalized artifacts:

- HTML sanitization and normalization
- DOM traversal with email-safe node classification
- Table/layout extraction
- Inline CSS parsing
- Snippet segmentation for reusable blocks
- Style fingerprint generation
- Formatting fingerprint generation

Outputs:

- Parsed document JSON
- Snippet library
- Style profile
- Formatting profile
- Retrieval records

### 4. AI Generation Pipeline

The generation pipeline uses deterministic RAG plus structured repair:

1. Ingest design reference and prompt.
2. Extract design cues from uploaded image or screenshot metadata.
3. Retrieve nearest training snippets based on structural/style similarity.
4. Build a canonical generation context in stable order.
5. Generate structured email plan first.
6. Generate HTML from the plan and retrieved examples.
7. Run normalization and email-safe validation.
8. Enter refinement loop using diff engine feedback.

Important design choices:

- Two-stage generation: plan first, HTML second, because it is more controllable than direct freeform code generation.
- Stable context ordering to preserve reproducibility.
- Rule-based guardrails for table nesting, inline CSS, widths, spacing, and fallback assets.

### 5. Diff Engine

The diff engine is multi-layered and intentionally non-magical.

#### A. Design Fidelity Diff

Measures visual similarity between uploaded design reference and rendered HTML preview:

- Layout bounding box comparison
- Spacing deltas
- Alignment deltas
- Typography heuristics
- Color similarity
- Section-by-section visual score
- Screenshot overlay mismatch detection

Outputs:

- Global design score
- Per-region mismatch list
- Suggested repairs

#### B. Developer Style Diff

Measures similarity between generated HTML and the developer's sample corpus:

- Table structure patterns
- Inline style ordering
- Attribute ordering
- Indentation and whitespace profile
- Comment usage pattern
- Naming conventions
- Snippet resemblance/confidence

Outputs:

- Global style score
- Per-rule style deviation list
- Formatter/rewriter suggestions

#### C. Refinement Loop

The loop combines both scores and iterates until thresholds or max iterations:

- Render current output
- Score design fidelity
- Score style mimicry
- Synthesize actionable deltas
- Apply targeted repair pass
- Re-score deterministically

Termination:

- Design score at or above threshold
- Style score at or above threshold
- Or max iteration count reached with explicit surfaced residual issues

### 6. Rendering System

Rendering must support both preview UX and machine comparison:

- HTML sandbox rendering in app
- Headless Chromium screenshot service
- DOM overlay map for element coordinates
- Click target mapping between preview and inspect panel
- Stable viewport presets for deterministic comparison

### 7. Inspect Panel System

The inspect panel behaves like lightweight DevTools specialized for emails:

- Click element in preview
- Resolve DOM node and canonical model node
- Show HTML path, attributes, inline styles, computed styles, dimensions
- Allow edits to text, attributes, styles, image source
- Show provenance: retrieved snippet sources and confidence values

Traceability implementation:

- Each generated block carries provenance metadata
- The renderer maps metadata to preview elements
- The inspect panel resolves the source chain without heuristics at click time

### 8. Assistant Engine

The assistant is a contextual local copilot, not a chat toy.

- Reads current project context
- Suggests fixes and best practices
- Runs micro-questionnaires to learn preferences
- Stores local preference profile and recent decisions
- Surfaces non-blocking recommendations in a bottom-right widget

Memory model:

- Project preferences
- User formatting/style preferences
- Accepted suggestions history
- Common asset replacement habits

### 9. Analytics Engine

The analytics system must be credible, not vanity math.

Metrics model:

- Estimated manual layout time
- Estimated debugging/rendering time
- Iteration cycles avoided
- Total generation/refinement duration
- Confidence score by run
- Historical trend line across projects

Exports:

- JSON summary
- CSV metrics
- Presentation-friendly report view

### 10. Determinism Strategy

Determinism is a first-class concern:

- Canonical input normalization
- Stable sorting of snippets and retrieval records
- Explicit versioning of prompts and rules
- Fixed temperature and seed when model supports it
- Rule-based post-processing to canonicalize formatting
- Snapshot-based regression tests on parsed models, generated HTML, and scores

## Milestone Plan

### Milestone 1: Product and Repo Foundation

Scope:

- Establish monorepo structure, package boundaries, shared tooling, and baseline scripts.

Key modules/files:

- `package.json`
- `pnpm-workspace.yaml`
- `turbo.json`
- `apps/web/*`
- `packages/contracts/*`
- `tsconfig*.json`

Acceptance criteria:

- Monorepo installs cleanly.
- Shared TypeScript config works across packages.
- `dev`, `build`, `test`, `lint`, and `export` script placeholders exist.

Verification steps:

- Run install successfully.
- Run `pnpm dev` and confirm app shell loads.
- Run `pnpm build`, `pnpm test`, and `pnpm lint`.

### Milestone 2: Local Runtime and One-Command Developer Experience

Scope:

- Ensure the entire stack runs locally with one command and sane defaults.

Key modules/files:

- `scripts/*`
- `.env.example`
- `README.md`
- app bootstrap config

Acceptance criteria:

- One command starts web app and local backing services.
- Missing env vars fail with actionable messages.

Verification steps:

- Run the single startup command on a fresh checkout.
- Validate first-run setup instructions from zero state.

### Milestone 3: Design System and Demo-Ready Shell

Scope:

- Build polished application shell, responsive layout, keyboard shortcuts, and core navigation.

Key modules/files:

- `packages/ui/*`
- `apps/web/app/*`
- `apps/web/components/layout/*`

Acceptance criteria:

- Workspace layout includes upload area, comparison region, inspect panel, assistant slot, and analytics route.
- Mobile and desktop layouts behave cleanly.

Verification steps:

- Manual responsive pass at desktop and tablet/mobile widths.
- Keyboard shortcut smoke test.

### Milestone 4: Shared Contracts and Domain Models

Scope:

- Define shared schemas for projects, assets, parsed emails, runs, diffs, provenance, and analytics.

Key modules/files:

- `packages/contracts/src/*`

Acceptance criteria:

- All critical API inputs/outputs are strongly typed and runtime-validated.

Verification steps:

- Contract unit tests pass.
- Invalid payloads fail schema validation.

### Milestone 5: Project Workspace and Asset Ingestion

Scope:

- Support upload and local persistence of HTML samples, screenshots, and supporting project metadata.

Key modules/files:

- ingestion APIs
- local storage adapters
- upload UI components

Acceptance criteria:

- Users can create a project, upload sample HTML and design references, and see stored assets.

Verification steps:

- Upload multiple HTML samples and one design image.
- Refresh app and confirm project reloads correctly.

### Milestone 6: HTML Email Parsing Engine

Scope:

- Parse uploaded HTML into canonical email structures, style fingerprints, and snippet segments.

Key modules/files:

- `packages/email-core/src/parser/*`
- normalization utilities

Acceptance criteria:

- Parser handles representative email HTML with nested tables and inline styles.
- Outputs canonical model and snippet segments.

Verification steps:

- Snapshot test parsed output for sample emails.
- Validate parser against malformed-but-common email HTML.

### Milestone 7: Style Fingerprinting and Developer Convention Learning

Scope:

- Learn indentation, ordering, formatting quirks, and reusable structures from uploaded samples.

Key modules/files:

- `packages/email-core/src/style-profile/*`
- formatting profile builders

Acceptance criteria:

- System produces stable developer style profiles from multiple samples.
- Profiles influence later formatting targets.

Verification steps:

- Run profile extraction twice on same inputs and confirm byte-identical outputs.
- Compare extracted conventions against hand-checked examples.

### Milestone 8: Local Retrieval and Snippet Indexing

Scope:

- Build snippet library, embedding/index persistence, similarity search, and deterministic retrieval ordering.

Key modules/files:

- `packages/retrieval/*`
- local SQLite/vector persistence

Acceptance criteria:

- Relevant snippets can be retrieved for a design/generation request.
- Retrieval is repeatable for identical inputs.

Verification steps:

- Seed sample corpus and run retrieval snapshots.
- Confirm stable ranking across repeated runs.

### Milestone 9: Design Reference Analysis Pipeline

Scope:

- Analyze image-based design inputs into structural hints and layout metadata suitable for generation.

Key modules/files:

- `packages/generator/src/design-analysis/*`
- image metadata extraction

Acceptance criteria:

- Design references are transformed into structured layout cues.
- Missing assets trigger placeholder planning.

Verification steps:

- Run design analysis on sample screenshots.
- Inspect generated layout cues manually against source image.

### Milestone 10: Deterministic HTML Generation Engine

Scope:

- Implement plan-first generation, snippet-conditioned HTML synthesis, and canonical serialization.

Key modules/files:

- `packages/generator/src/orchestrator/*`
- prompt templates
- HTML serializer

Acceptance criteria:

- System generates valid HTML email output from prompt + design + training examples.
- Same input yields same output under deterministic mode.

Verification steps:

- Snapshot generated HTML for fixed fixtures.
- Re-run generation multiple times and compare hashes.

### Milestone 11: Rendering and Live Preview System

Scope:

- Render generated HTML reliably in-app and through headless screenshots for machine scoring.

Key modules/files:

- `packages/rendering/*`
- preview components
- screenshot service

Acceptance criteria:

- Live preview matches stored HTML.
- Render pipeline produces consistent screenshots for diffing.

Verification steps:

- Compare repeated screenshots for stability.
- Manual preview validation with representative email fixtures.

### Milestone 12: Design Fidelity Diff Engine

Scope:

- Implement visual comparison between rendered email and design reference with actionable mismatch output.

Key modules/files:

- `packages/diff-engine/src/design-diff/*`

Acceptance criteria:

- System produces a global score and per-region mismatch report.

Verification steps:

- Run diff fixtures with known spacing/color/layout mismatches.
- Confirm score degrades in expected direction.

### Milestone 13: Developer Style Diff Engine

Scope:

- Implement code-style similarity scoring against developer samples.

Key modules/files:

- `packages/diff-engine/src/style-diff/*`

Acceptance criteria:

- System scores structural and formatting similarity in a transparent way.

Verification steps:

- Evaluate intentionally restyled outputs against original corpus.
- Confirm style score tracks known deviations.

### Milestone 14: Self-Correction and Refinement Loop

Scope:

- Wire generation, rendering, design diff, and style diff into an automated iterative correction loop.

Key modules/files:

- `packages/generator/src/refinement/*`
- run orchestration APIs

Acceptance criteria:

- Loop iterates automatically and stops on thresholds or max passes.
- Run summary includes design and style scores per iteration.

Verification steps:

- Execute fixed fixture end-to-end.
- Confirm loop improves score monotonically or reports why not.

### Milestone 15: Comparison Workspace

Scope:

- Build split-view workspace for design, preview, code, and overlay diff mode.

Key modules/files:

- comparison UI components
- overlay rendering components

Acceptance criteria:

- Users can switch between split, stacked, and overlay views.
- Mismatches are visible and navigable.

Verification steps:

- Manual UX pass on sample projects.
- Check overlay alignment with known mismatch fixtures.

### Milestone 16: Code Editor and Live Sync

Scope:

- Add syntax-highlighted HTML editor with live preview synchronization and formatting preservation.

Key modules/files:

- editor components
- code synchronization services

Acceptance criteria:

- Editing code updates preview quickly.
- Formatting is preserved unless explicit normalization is requested.

Verification steps:

- Manual edit-preview roundtrip.
- Snapshot preservation tests for unchanged sections.

### Milestone 17: Inspect Panel and Provenance Traceability

Scope:

- Implement element inspection, editable properties, and snippet provenance/confidence display.

Key modules/files:

- inspect panel UI
- DOM mapping services
- provenance metadata integration

Acceptance criteria:

- Clicking preview elements reveals structure, styles, dimensions, and source influence.
- Edits apply immediately and persist in workspace state.

Verification steps:

- Click-through test on representative generated email.
- Validate provenance references against retrieval logs.

### Milestone 18: Intelligent Placeholder Asset System

Scope:

- Insert `https://placehold.co` PNG placeholders with correct dimensions when learned assets are unavailable.

Key modules/files:

- asset resolution module
- inspect panel image replacement controls

Acceptance criteria:

- Placeholder assets preserve layout integrity.
- Users can replace them from inspect panel.

Verification steps:

- Generate fixture with missing assets.
- Confirm dimensions and replacement workflow.

### Milestone 19: Assistant Widget and Preference Learning

Scope:

- Build floating assistant, suggestion engine, micro-questionnaires, and persistent local preference memory.

Key modules/files:

- `packages/assistant/*`
- widget UI components

Acceptance criteria:

- Assistant gives context-aware suggestions without blocking workflow.
- User preferences persist across sessions.

Verification steps:

- Accept and reject suggestions, then reload app.
- Confirm preferences influence future recommendations.

### Milestone 20: Analytics Dashboard and Export System

Scope:

- Build results dashboard with time saved metrics, trends, confidence, and export/share outputs.

Key modules/files:

- `packages/analytics/*`
- dashboard route/components
- export scripts

Acceptance criteria:

- Dashboard shows run history and estimated savings with transparent formulas.
- Exports work in local mode.

Verification steps:

- Generate multiple runs and confirm trend aggregation.
- Export JSON/CSV and verify content correctness.

### Milestone 21: Quality Gates, Regression Suite, and Release Hardening

Scope:

- Add comprehensive tests, fixture packs, lint rules, CI-style local checks, and demo defaults.

Key modules/files:

- test suites across packages
- fixture datasets
- release scripts

Acceptance criteria:

- Core pipelines are covered by unit/integration/regression tests.
- Demo project ships ready to run locally.

Verification steps:

- Run full test suite.
- Execute demo script from fresh environment.

## Risk Register

### Risk 1: Visual Diff Accuracy

Why it matters:

- Pixel-perfect comparison can be noisy due to rendering differences, anti-aliasing, and image scaling.

Mitigation:

- Use normalized viewport presets.
- Combine image diff with structural layout heuristics.
- Score by regions, not just full-frame pixels.

Fallback:

- Surface confidence bands and mismatch categories rather than pretending false precision.

### Risk 2: Style Mimicry Accuracy

Why it matters:

- Developers notice formatting and structural quirks instantly; generic prettified output will fail trust.

Mitigation:

- Extract explicit style/formatting profiles.
- Use rule-based post-processing in addition to AI generation.
- Build transparent style-diff scoring.

Fallback:

- Allow strict style mode that prioritizes sample-derived formatting over broader optimization.

### Risk 3: HTML Email Rendering Inconsistencies

Why it matters:

- HTML email behaves differently across clients and is less forgiving than normal web rendering.

Mitigation:

- Center architecture on table-safe markup and inline CSS.
- Add validation rules for email-safe patterns.
- Preserve reusable patterns from real training emails.

Fallback:

- Ship compatibility warnings and lint feedback for risky constructs.

### Risk 4: Deterministic Output Challenges

Why it matters:

- AI generation can drift even with the same inputs, undermining trust and reproducibility.

Mitigation:

- Canonicalize inputs and retrieval order.
- Fix model parameters where supported.
- Add deterministic serializer and post-processing stages.

Fallback:

- Expose deterministic mode and document any model/provider limitations clearly.

### Risk 5: Provenance Mapping Complexity

Why it matters:

- Snippet traceability must remain accurate after refinement passes and manual edits.

Mitigation:

- Store provenance at block level with stable IDs.
- Re-map edits through canonical model nodes instead of raw string offsets.

Fallback:

- Degrade gracefully to block-level provenance if element-level certainty drops.

### Risk 6: Local-First Performance

Why it matters:

- Rendering, screenshotting, retrieval, and multi-pass refinement can become sluggish on laptops.

Mitigation:

- Use background jobs and incremental caching.
- Cache parsed samples, rendered screenshots, and diff intermediates.

Fallback:

- Offer quality presets for faster demo mode vs deeper engineering mode.

## Verification Strategy

Each milestone will include explicit verification, but the broader strategy is:

- Unit tests for parsers, schema validators, scoring rules, and serializers
- Integration tests for upload-to-generation and generate-to-refine flows
- Snapshot tests for parsed structures, generated HTML, and deterministic outputs
- Visual regression tests for preview and diff features
- Manual demo scripts for high-confidence stakeholder presentation

## Demo Script

### Goal

Demonstrate that the product is both easy to understand for non-technical viewers and clearly sophisticated for engineers.

### 3-Minute Flow

#### Minute 0:00 to 0:30 — Project Setup

- Open the app to a polished demo project.
- Show uploaded sample emails and one target design reference.
- Explain that the system has already learned developer-specific email patterns.

#### Minute 0:30 to 1:10 — Generate

- Enter a short prompt or select the design reference.
- Trigger generation.
- Show the pipeline status: retrieval, plan creation, HTML generation, render, and refinement.

#### Minute 1:10 to 1:50 — Refine and Compare

- Open comparison workspace with design, preview, and code side-by-side.
- Toggle overlay diff to highlight mismatches.
- Show design similarity and style similarity scores improving across iterations.

#### Minute 1:50 to 2:30 — Inspect and Edit

- Click a hero block or CTA in preview.
- Open inspect panel showing HTML, styles, dimensions, and training snippet provenance.
- Swap an image placeholder and tweak copy live.

#### Minute 2:30 to 3:00 — Results and Value

- Open analytics dashboard.
- Show estimated time saved, refinement cycles avoided, confidence score, and export options.
- Close by emphasizing deterministic, local-first, production-ready architecture.

## Delivery Standards

The final repository must include:

- Fully working local web app
- Demo-ready seed project
- Shared contracts and modular packages
- `plans.md`
- Architecture documentation
- Scripts for `dev`, `build`, `test`, `lint`, and `export`
- Clear verification steps per milestone

## Implementation Guardrails

- No implementation starts before this plan is accepted as coherent.
- Each milestone should land in a testable state.
- UX polish is not deferred to the end; it is continuous.
- Determinism and traceability take precedence over flashy but opaque AI behavior.
