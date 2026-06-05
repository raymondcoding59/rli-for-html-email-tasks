# TITLE
Iteration 2: Deterministic Band Expansion and Token Observability

## HYPOTHESIS
If visually merged design sections are deterministically expanded into DWR-like top-level bands before generation, the output should better match the target's wrapper rhythm and section count. Adding descriptive comments and full token accounting should also make the script easier to audit and compare across experiments.

## CHANGES MADE
- Chunking: kept experiment 1's reference-native top-level DWR band chunking.
- Design extraction: added deterministic expansion of merged design sections into stable section families such as `brand_header`, `copy_block`, `image_band`, `two_column_image_grid`, and split footer bands.
- Layout extraction: retained DWR-aware fingerprints for wrappers, full-width images, outline buttons, and social rows.
- Retrieval: retained section-family alias scoring and now runs against the expanded section plan.
- Prompting: section prompts now receive more granular target sections after normalization.
- Generation: each generated section token log has a descriptive name containing section index and type.
- Assembly: unchanged deterministic shell assembly from experiment 1.
- Normalization: added `clone_section()`, `canonical_section_type()`, and `expand_design_section()` to split visually merged sections without target-aware HTML patching.
- Evaluation: unchanged weighted scoring framework.
- Observability: added descriptive docstrings/comments across the script and expanded README token totals with grand total input, output, and combined tokens.

## RESULTS
The run generated `output.html`, `chunks/`, raw and normalized design specs, process logs, README token logs, and `evaluation.json`. The normalized design plan is now more granular before generation, which directly tests whether deterministic band expansion improves target alignment.

Improvements observed:
- README token logging now includes descriptive call names and grand totals for input, output, and combined tokens.
- The script is more readable because each major function now explains its role.
- The generated structure can be evaluated against a more target-like section plan.
- Overall similarity can improve even when structure needs more calibration, because content/style/reuse may benefit from more granular prompts.

Failures/regressions:
- Section expansion increases the number of model calls, so token use can rise.
- More granular prompts may improve structure while risking lighter individual section content.
- Deterministic expansion can overshoot the target section count when the visual extractor already split some image/copy bands.
- This still does not perform target-aware deterministic HTML patching, so literal 100% similarity remains unlikely.

## EVALUATION
- Structural similarity: `18.6 / 30`
- Content accuracy: `23.61 / 25`
- Component fidelity: `15.0 / 20`
- Style fidelity: `19.62 / 20`
- Reuse of learned assets/patterns: `4.38 / 5`

Similarity score: `81.21 / 100`

Qualitative analysis:
The evaluation measures whether the expanded design plan better follows the DWR target's top-level wrapper rhythm. Component, content, and style scores show whether the extra structure helped without thinning out the generated HTML.

Metric breakdown:
- Output sections: `5`; target sections: `2`
- Output images: `5`; target images: `8`
- Output links: `9`; target links: `12`
- Output table count: `30`; target table count: `30`

## ANALYSIS
Experiment 1 showed that the biggest remaining structural gap was not reference chunk quality but visual extraction granularity. The model saw the design correctly at a high level, but merged several bands that the target implements as separate DWR wrapper tables. This experiment moves that correction into deterministic normalization, where it is cheaper and more stable than asking generation prompts to infer missing band boundaries.

The approach remains generalizable because it splits on broad structural signals: logo images paired with copy, two-column image grids with a trailing CTA, image-and-copy sections, and footer contact/legal groupings.

The next version should keep deterministic expansion but calibrate it against the expected wrapper rhythm so it does not over-split.

## NEXT STEPS
1. Calibrate deterministic expansion to the expected DWR wrapper rhythm so it does not over-split.
2. Canonicalize remaining extractor aliases such as `main_image`, `feature_text`, and `secondary_cta`.
3. Add deterministic image asset selection from `image_memory` to avoid invented image URLs.
4. Add a deterministic reference-pattern assembler for common DWR section families, replacing only text, href/reporting labels, colors, and image assets inside selected reference chunks.
