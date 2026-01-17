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
- Use the @import rule to import any web fonts.


### Spacing, Margins & Paddings
- Do not create a separate spacing element. Always use the "td tag" top-padding of the lower section/element to create the spacing between two sections/elements. For the first element/section in a pile, use its top-padding, and for the last element/section in a pile, use its top-padding and bottom-padding. For texts always use the top-margin of the "p tag" containing each paragraph for spacing, applying the same pile rules for the first and last paragraphs in a copy section.

- Do not apply the email's left and right padding to the email container, rather apply it to each section individually, in their outermost "td tag".

- Some Sections/elements like full-width images already have the right and left padding baked in, so confirm before applying padding.

### Images
- Use placehold.co image placeholders for all images and icons whose source urls are not specified(with .png image type, background colour as the inferred background of the image, and text color as the inferred text color of the image).


## SPECIFICATIONS

**Email Background**
- background-color: #F3F2F0
- width: 100%

-------------
Spacing: 8px, on mobile and desktop
-------------

**Email Container**
- width: 512px
- background-color: #FFFFFF 



**Logo**
- Dimensions: 84x21
- element type: image
- responsive: false
- Alignment: left
- destination url: "#"
- source: https://static.licdn.com/aero-v1/sc/h/9ehe6n39fa07dc5edzv0rla4e


**Profile picture**
- Dimensions: 32x32
- element type: image
- responsive: false
- Alignment: right
- destination url: "#"
- source: 

-------------
Spacing: 36px
-------------

**Headline**
SECTION RIGHT AND LEFT PADDING: 24px
PARAGRAPHS SPACING: Null
margin: 0;
font-size: 24px;
font-weight: 600;
line-height: 1.25;
color: #282828;
font-family: -apple-system, system-ui, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', 'Fira Sans', Ubuntu, Oxygen, 'Oxygen Sans', Cantarell, 'Droid Sans', 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', 'Lucida Grande', Helvetica, Arial, sans-serif;

-------------
Spacing: 12px
-------------


**text**
SECTION RIGHT AND LEFT PADDING: 24px
PARAGRAPHS SPACING: Null
margin: 0;
font-weight: 400 and 700;
font-size: 14px;
color: #000000e6;
font-family: -apple-system, system-ui, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', 'Fira Sans', Ubuntu, Oxygen, 'Oxygen Sans', Cantarell, 'Droid Sans', 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', 'Lucida Grande', Helvetica, Arial, sans-serif;

-------------
Spacing: 24px
-------------


**Stat Cards**
border-radius: 4px;
background-color: #f7f7f7;
padding-left: 12px;
padding-right: 12px;
padding-top: 16px;
padding-bottom: 16px;
border-top: 3px solid #01754f;
height: 100%;

number
margin: 0;
font-size: 20px;
font-weight: 600;

label
margin: 0;
font-weight: 400;
font-size: 14px;

Spacing between cards: 12px



-------------
Spacing: 12px
-------------


**text**
SECTION RIGHT AND LEFT PADDING: 24px
PARAGRAPHS SPACING: Null
margin: 0;
font-weight: 400 and 700;
font-size: 14px;
color: #000000e6;
font-family: -apple-system, system-ui, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', 'Fira Sans', Ubuntu, Oxygen, 'Oxygen Sans', Cantarell, 'Droid Sans', 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', 'Lucida Grande', Helvetica, Arial, sans-serif;

-------------
Spacing: 24px
-------------

**Button**
SECTION RIGHT AND LEFT PADDING: 24px
BUTTON ALIGNMENT: LEFT
color: #ffffff;
text-decoration-line: none;
display: inline-block;
text-decoration: none;
vertical-align: top;
-webkit-text-size-adjust: 100%;
-ms-text-size-adjust: 100%;
mso-table-lspace: 0pt;
mso-table-rspace: 0pt;
height: min-content;
border-radius: 24px;
padding-top: 12px;
padding-bottom: 12px;
padding-left: 24px;
padding-right: 24px;
text-align: center;
font-size: 16px;
font-weight: 600;
cursor: pointer;
background-color: #0a66c2;
border-width: 1px;
border-style: solid;
border-color: #0a66c2;
line-height: 1.25;
min-height: auto !important;
box-shadow: 0 0 #0000, 0 0 #0000, 0 0 #0000 !important;
destination url: #

