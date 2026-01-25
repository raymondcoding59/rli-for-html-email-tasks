# Prompt
Convert this email design into a pixel-perfect HTML email that is compatible with all email clients, mobile-responsive, and dark-mode friendly. 


Use the following instructions and specifications.


## INSTRUCTIONS

### General
- Specifications for non-mentioned elements can be inferred from the design.
- When in doubt, use the design as the ultimate source of truth.

### Styles
- Use inline CSS as much as possible. Use the style tag for the other declarations such as fonts, responsive, and dark mode styles.

### Fonts
- Use the @import rule to import any mentioned web fonts.


### Spacing, Margins & Paddings
- Do not create a separate spacing element. Always use the "td tag" top-padding of the lower section/element to create the spacing between two sections/elements. For the first element/section in a pile, use its top-padding, and for the last element/section in a pile, use its top-padding and bottom-padding. For texts always use the top-margin of the "p tag" containing each paragraph for spacing, applying the same pile rules for the first and last paragraphs in a copy section.

- Do not apply the email's left and right padding to the email container, rather apply it to each section individually, in their outermost "td tag".

- Some Sections/elements like full-width images already have the right and left padding baked in, so confirm before applying padding.

### Images
- Use placehold.co image placeholders for all images and icons whose source urls are not specified(with .png image type, background colour as the inferred background of the image, and text color as the inferred text color of the image).


## SPECIFICATIONS

**Email Background**
- background-color: #F5F5F5
- width: 100%

-------------
Spacing: 32px, on desktop only
-------------

**Email Container**
- width: 600px
- background-color: #FFFFFF 



**Logo Banner**
- Dimensions: 600x105
- element type: image
- make responsive: yes
- Alignment: center
- destination url: "#"
- source: https://mktgimages.opentable.com/2026/Paid/20260107_AthelticLogo.png


-------------
Spacing: 4px
-------------



**Eyebrow**
SECTION RIGHT AND LEFT PADDING: 80px desktop, 48px mobile
PARAGRAPHS SPACING: Null
font-family: sans-serif;
font-size: 16px;
line-height: 16px;
font-weight: 600;
color: #0C0C0B;
text-transform: uppercase;
background-color: #FFFFFF;
text-decoration: none;
destination url: #

-------------
Spacing: 24px
-------------



**Divider line**
SECTION RIGHT AND LEFT PADDING: 80px desktop, 48px mobile
height: 2px;
border-width: 0;
color: #0C0C0B;
background-color: #0C0C0B;


-------------
Spacing: 40px
-------------

**Headline**
SECTION RIGHT AND LEFT PADDING: 80px desktop, 48px mobile
PARAGRAPHS SPACING: Null
IS HYPERLINKED: TRUE
font-family: serif;
font-size: 48px;
line-height: 54px;
font-weight: 400;
color: #0C0C0B;
background-color: #FFFFFF;
text-decoration: none;
destination url: #

-------------
Spacing: 16px
-------------


**Body copy**
SECTION RIGHT AND LEFT PADDING: 80px desktop, 48px mobile
PARAGRAPHS SPACING: Null
IS HYPERLINKED: TRUE
font-family: sans-serif;
font-size: 20px;
line-height: 28px;
font-weight: 300;
color: #0C0C0B;
text-decoration: none;
background-color: #FFFFFF;
destination url: #

-------------
Spacing: 24px
-------------

**Button**
SECTION RIGHT AND LEFT PADDING: 80px desktop, 48px mobile
BUTTON ALIGNMENT: CENTER
font-family: sans-serif;
font-size: 16px;
line-height: 48px;
font-weight: 600;
color: #FFFFFF;
background-color: #0C0C0B;
text-align: center;
text-decoration: none;
width: 100%;
-webkit-text-size-adjust: none;
mso-hide: all;
display: inline-block;
destination url: #

-------------
Spacing: 24px
-------------