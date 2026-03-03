```markdown
# METHODICAL EMAIL DESIGN SYSTEM  
**Derived from Sample Design + Production HTML Structure**  
Source reference: Sample HTML Email Code :contentReference[oaicite:0]{index=0}

---

# 1. SYSTEM OVERVIEW

This design system documents **visual rules + structural HTML patterns** used in the provided email so any junior developer can recreate future campaigns **matching BOTH design intent and Klaviyo/MJML output structure**.

The email follows:

✅ Klaviyo-generated hybrid MJML table architecture  
✅ 600px fixed desktop container  
✅ Fully stacked mobile layout  
✅ Image-led storytelling  
✅ Editorial + commerce hybrid format  

---

# 2. GLOBAL EMAIL ARCHITECTURE

## Canvas Structure

```

<body bgcolor="#EEECE8">
  root-container
    root-container-spacing
      SECTION
        600px centered container
          content blocks
```

### Width Rules

| Element            | Width     |
| ------------------ | --------- |
| Email max width    | **600px** |
| Inner content      | 550px     |
| Edge bleed imagery | 600px     |
| Mobile             | 100%      |

---

# 3. COLOR SYSTEM

## Primary Palette

| Token              | Color     | Usage              |
| ------------------ | --------- | ------------------ |
| Background Outer   | `#EEECE8` | Inbox canvas       |
| Content Background | `#FFFAF3` | Main email body    |
| Primary Text       | `#3E3A37` | Headlines/body     |
| CTA Brown          | `#8B7351` | Primary buttons    |
| Accent Link        | `#8A501D` | Product titles     |
| Divider            | `#CCCCCC` | Section separators |
| Footer Background  | `#363A4A` | Footer             |
| White              | `#FFFFFF` | Secondary buttons  |

---

# 4. TYPOGRAPHY SYSTEM

## Font Stack

### Editorial Serif (Headlines)

```
"Canela Text",
Palatino,
Georgia,
serif
```

Used for:

* H1
* H2
* H3
* Section titles

---

### Functional Sans (UI + Body)

```
"Hanken Grotesk",
Helvetica,
Arial,
sans-serif
```

Used for:

* Body copy
* Buttons
* Product names
* Navigation

---

## Type Scale

| Element       | Size | Weight | Line Height |
| ------------- | ---- | ------ | ----------- |
| H1            | 45px | 300    | 1           |
| H2            | 35px | 300    | 1.3         |
| H3            | 28px | 300    | 1.3         |
| Eyebrow       | 18px | 600    | 1.3         |
| Body          | 18px | 300    | 1.5         |
| Product Title | 16px | 600    | 1.5         |
| Button        | 18px | 600    | 1           |

### Mobile Overrides

```
H1 → 35px
H2 → 28px
H3 → 22px
Body → 14px
```

---

# 5. SPACING SYSTEM

Spacing is **table padding-driven**.

## Vertical Rhythm Tokens

| Token         | Value   |
| ------------- | ------- |
| XS            | 9px     |
| SM            | 18px    |
| MD            | 25px    |
| LG            | 32px    |
| XL            | 45–50px |
| Footer Bottom | 60px    |

---

## Content Padding Pattern

```
<td style="padding:18px 25px;">
```

Golden rule:

> All readable content lives inside **25px side padding**

---

# 6. LAYOUT COMPONENTS

---

## 6.1 HERO IMAGE BLOCK

### Structure

```
SECTION
 └ full-width image (600px)
```

### Rules

* Always clickable
* Display:block
* Width:100%
* No side padding
* Acts as visual headline

---

## 6.2 TEXT INTRO BLOCK

Pattern:

```
Text
Text
CTA Button
Divider
```

Body alignment:

```
text-align:left
```

Max readability width achieved via padding container.

---

## 6.3 DIVIDER

HTML Pattern:

```
<p style="border-top:1px solid #CCC;"></p>
```

Rules:

* Always centered
* Full container width
* Used between narrative sections

---

# 7. BUTTON SYSTEM

Buttons use **bulletproof table buttons**.

---

## Primary Button

### Visual

* Filled background
* No border
* Full width

### Specs

| Property       | Value   |
| -------------- | ------- |
| BG             | #8B7351 |
| Text           | White   |
| Padding        | 25px    |
| Radius         | 0       |
| Letter spacing | 1px     |

---

## Secondary Button (Outlined)

| Property | Value             |
| -------- | ----------------- |
| BG       | White             |
| Border   | 2px solid #3E3A37 |
| Text     | #3E3A37           |

---

### Button HTML Pattern

```
<table>
 <tr>
  <td bgcolor="">
   <a display:inline-block padding:25px 0>
```

RULE:

> Anchor controls typography. TD controls background.

---

# 8. MEDIA / VIDEO BLOCK

Implemented as:

✅ Static image
✅ Play overlay baked into image
✅ Linked externally

Never embed video.

Width:

```
500px centered
```

---

# 9. PRODUCT GRID SYSTEM

## Layout

2-column responsive grid.

Desktop:

```
50% | 50%
```

Mobile:

```
Stacked 100%
```

---

## Product Card Anatomy

```
Product Cell
 ├ Image
 ├ Product Name Link
 └ Spacer
```

### Image Rules

* Max height: 200px
* Center aligned
* Auto width

### Product Title

```
16px
600 weight
Accent color
Underlined link
```

---

# 10. CATEGORY TILE GRID

Uses table grid (NOT columns).

```
2 x 2 image matrix
```

Each tile:

* 300px width
* Edge-to-edge imagery
* Text embedded in image asset

Padding:

```
1px gutters
```

Purpose:
Creates seamless collage effect.

---

# 11. FOOTER SYSTEM

## Background

```
#363A4A
```

## Structure

```
Logo
Support Text
Social Icons
Utility Links
Address
```

### Footer Text

| Style | Value   |
| ----- | ------- |
| Color | #CED2E0 |
| Align | Center  |
| Size  | 14–16px |

---

# 12. RESPONSIVE RULES

Mobile breakpoint:

```
max-width:480px
```

Key behaviors:

✅ Columns stack
✅ Images become fluid
✅ Padding reduced
✅ Font sizes scale down
✅ Buttons remain full-width

Critical Class:

```
kl-row colstack
```

---

# 13. IMAGE RULES

Always:

```
display:block;
max-width:100%;
height:auto;
```

Never rely on CSS margins.

Spacing handled by parent TD.

---

# 14. ACCESSIBILITY STANDARDS

Required:

✅ Alt text on all images
✅ Meaningful CTA copy
✅ 16px+ body equivalent
✅ High contrast buttons
✅ Linked images duplicated by text CTA nearby

---

# 15. PREHEADER SYSTEM

Hidden preview text block:

```
display:none;
max-height:0;
opacity:0;
overflow:hidden;
```

Used to control inbox preview.

---

# 16. DEVELOPMENT GUIDELINES

## MUST FOLLOW

✔ Table-based layout only
✔ Inline styles preferred
✔ Avoid margin usage
✔ Padding via TD
✔ No position:absolute
✔ No background images critical to UX

---

## SECTION BUILD ORDER

1. Preheader
2. Hero
3. Intro Copy
4. Primary CTA
5. Divider
6. Educational Block
7. Media
8. Secondary CTA
9. Product Grid
10. Shop CTA
11. Category Grid
12. Footer

---

# 17. REUSABLE COMPONENT LIBRARY

| Component       | Reusable |
| --------------- | -------- |
| Hero Image      | ✅        |
| Text Block      | ✅        |
| Divider         | ✅        |
| Primary Button  | ✅        |
| Outline Button  | ✅        |
| Video Thumbnail | ✅        |
| Product Grid    | ✅        |
| Category Matrix | ✅        |
| Footer          | ✅        |

---

# 18. QA CHECKLIST

Before deployment:

* [ ] Email width = 600px
* [ ] Images fluid
* [ ] Buttons clickable full area
* [ ] Mobile stacking verified
* [ ] Outlook rendering tested
* [ ] Links underlined where expected
* [ ] Alt text present
* [ ] Padding consistent (25px rule)

---

# ✅ CORE PRINCIPLE

> **Editorial storytelling first. Commerce second.
> Structure must feel like a magazine — built with tables.**

This system ensures future emails visually and structurally match the provided production template while remaining fully scalable.

```
```
