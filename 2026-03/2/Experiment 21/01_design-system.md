Below is a Design System in markdown, reverse-engineered from your supplied HTML email code.



✨ HTML Email Design System

Colors

| Name             | Hex        | Usage                                            |
|------------------|-----------|--------------------------------------------------|
| Background       | #EEECE8 | Root <body>, containers, page backgrounds      |
| Panel            | #FFFAF3 | Main content card/panel                          |
| Text - Primary   | #3E3A37 | Primary headings, body text                      |
| Link             | #CED2E0 | Links, emphasized navigational elements          |
| Button (Default) | not present | (Add as needed; typical for brand color)      |



Typography

Font Families


Serif Headings:

"Canela Text", Palatino, "Palatino Linotype", "Palatino LT STD", "Book Antiqua", Georgia, serif

Sans-serif Subheadings:

"Hanken Grotesk", Helvetica, Arial, sans-serif


Font Sizes & Weights

| Element      | Font family      | Size (px) | Weight | Line Height | Style     | Letter Spacing | Responsive         |
|--------------|-----------------|-----------|--------|-------------|-----------|----------------|--------------------|
| h1           | Serif           | 45        | 300    | 1           | Normal    | 0              | 35px @ ≤480px      |
| h2           | Serif           | 35        | 300    | 1.3         | Normal    | 0              | 28px @ ≤480px      |
| h3           | Serif           | 28        | 300    | 1.3         | Normal    | 0              | 22px @ ≤480px      |
| h4           | Sans-serif      | 18        | 600    | 1.3         | Normal    | 2px            | 14px @ ≤480px      |
| Body (p)     | Not explicit    | 16*       | 400    | Normal      |           |                | 14px @ ≤480px      |
| Links (a)    | Inherit         | Inherit   | Inherit| Inherit     |           |                |                    |


*Best guess for default copy based on conventions and media queries.



Spacing

General

| Token                       | Value (px) | Usage                                           |
|-----------------------------|------------|-------------------------------------------------|
| Section Vertical Padding    | 50 / 20    | Top/bottom root section (root-container-spacing)|
| Card Content Padding        | 20         | Content outside card image area                  |
| Gutter / Side Padding       | 18         | For columns on mobile (see .kl-text)           |
| Element Margin (Vert.)      | 24         | Headings (h2, h3)                             |
| Element Margin (Vert.)      | 12         | h4                                            |
| Paragraph Bottom Margin     | 13         | p tags (margin: 13px 0)                     |
| Paragraph Padding Bottom    | 1em        | padding-bottom on p                         |
| Image Padding Bottom        | 25         | Card image (padding-bottom:25px)               |


Responsive


On mobile (max-width:480px):

Root container section padding reduces to 10px

Content side padding to 0 (edge-to-edge content), text gets 18px side padding





Components

1. Card / Panel


BG: #FFFAF3

Border radius: 0 (flat)

Max-width: 600px (centered in the container)

Padding: 20px on desktop; 0 on mobile

Image: Full-width, scales responsively


2. Image


Width: 100% (with max of 600px)

Alt/title: Descriptive

Spacing: 0 padding except bottom (25px)

Link: Wrapped in link, uses link color


3. Text Block


Padding: 0 on desktop, 18px sides on mobile

Inherits: Typography settings above


4. Section / Container


BG: #EEECE8

Spacing: 50px top, 20px bottom (root padding on desktop)

Max-width: 600px


5. Link


Color: #CED2E0

Decoration: Underline, always

States: All states share same color



Buttons


⚠️ Not fully shown in the supplied code, but standard email button conventions can be inferred. Add/adjust as needed.



Recommended Button Styles:


| Property      | Value         |
|---------------|--------------|
| Bg color      | Primary brand |
| Text color    | #3E3A37 (or white) |
| Padding       | 16px 32px    |
| Border radius | 0            |
| Font size     | 16px         |
| Font weight   | 600          |
| Font family   | "Hanken Grotesk", Helvetica, Arial, sans-serif|
| Text-align    | Center       |
| Border        | None         |
| Link style    | No underline |



Layout Rules


Max container width: 600px (centered)

All content centered horizontally unless overridden

Images are fluid (100% width, auto height, max-width:600px)

All text centered

Section backgrounds always extend to 100% viewport width (background color classes on containers)

Cards / panels have a soft off-white background Inside the root section

Responsive:

On mobile (≤480px):

Padding and font sizes are reduced

All columns/sections stack vertically (full width)

Side paddings are removed (content edge-to-edge if needed)

Text & images center-aligned







Accessibility


All images have descriptive alt and title attributes

Contrast for text color (#3E3A37 on #FFFAF3 and #EEECE8) passes basic accessibility



Example: Email Card Layout (Abstracted)

<div style="background:#EEECE8;padding:50px 0 20px 0;">
  <center>
    <div style="background:#FFFAF3;max-width:600px;margin:auto;">
      <a href="LINK"><img src="IMAGE.png" width="600" style="width:100%;max-width:600px;display:block;"></a>
      <h1>Heading</h1>
      <p>Body content here</p>
      <a href="LINK" style="color:#CED2E0;text-decoration:underline;">Link text</a>
      <div style="margin:32px 0">
        <a href="LINK" style="background:BRAND_COLOR;color:#3E3A37;padding:16px 32px;
          font:600 16px 'Hanken Grotesk',Arial,sans-serif;text-decoration:none;
          border-radius:0;display:inline-block;text-align:center;">Button Text</a>
      </div>
    </div>
  </center>
</div>


Summary Table

| Element      | BG      | Max-width | Align | Font           | Size | Padding            | Border | Responsive     |
|--------------|---------|-----------|-------|----------------|------|--------------------|--------|---------------|
| Section      | #EEECE8 | 100%      | center| N/A            | N/A  | 50/20px top/bottom | none   | 10px on mobile|
| Panel/Card   | #FFFAF3 | 600px     | center| See headings   |      | 20px (content)     | 0      | 0 on mobile   |
| Heading h1   | N/A     | 600px     | center| Serif          | 45px | 0                  | 0      | 35px on mobile|
| Heading h2   | N/A     | 600px     | center| Serif          | 35px | 0                  | 0      | 28px on mobile|
| h3, h4, p    | N/A     | 600px     | center| As styled      |      | 0                  |        | See above     |
| Image        | N/A     | 600px     | center| N/A            | N/A  | 0/25px bottom      | 0      | fluid         |
| Link         | N/A     | N/A       | N/A   | As surrounding | N/A  | N/A                | N/A    | N/A           |



Usage Notes


All typography and layout are mobile-optimized: headline and content shrink gracefully on mobile.

Use containers for card layouts; background colors create strong separation between root and content.

Spacing tokens should be applied consistently to maintain rhythm and clarity.

All "buttons," where present, appear as colored links styled to occupy a block or inline-block (see above).



Adapt this system to cover additional needs such as product components, footers, etc. as required by your email campaign.



End of Design System