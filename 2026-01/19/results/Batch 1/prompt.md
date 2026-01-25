# Prompt
Convert this email design into a pixel-perfect HTML email that is compatible with all email clients, mobile-responsive, and dark-mode friendly. 


Use the following instructions and specifications.


## INSTRUCTIONS

### General
- Specifications for non-mentioned elements can be inferred from the design.
- When in doubt, use the design as the ultimate source of truth.
- use the attached structure.html as the a guide for the HTML email structure.

### Styles
- Use inline CSS as much as possible. Use the style tag for the other declarations such as fonts, responsive, and dark mode styles.

### Fonts
- Use the @import rule to import any mentioned web fonts.


### Spacing, Margins & Paddings
- Do not create a separate spacing element. Always use the "td tag" top-padding of the lower section/element to create the spacing between two sections/elements. For the first element/section in a pile, use its top-padding, and for the last element/section in a pile, use its top-padding and bottom-padding. For texts always use the top-margin of the "p tag" containing each paragraph for spacing, applying the same pile rules for the first and last paragraphs in a copy section.

- If you create ANY empty spacer rows or spacing-only elements, the output is invalid.

- Do not apply the email's left and right padding to the email container, rather apply it to each section individually, in their outermost "td tag".

- Some Sections/elements like full-width images already have the right and left padding baked in, so confirm before applying padding.

### Images
- Use placehold.co image placeholders for all images and icons whose source urls are not specified(with .png image type).


## SPECIFICATIONS

**Email Background**
- background-color: #EEEEEE
- width: 100%


**Email Container**
- width: 600px
- background-color: #FFFFFF 


-------------
Spacing: 12px
-------------


**Logo**
- Dimensions: 75x21
- element type: image
- make responsive: no
- Alignment: center
- destination url: "#"
- source: https://braze-images.com/appboy/communication/assets/image_assets/images/64ad8252f2eaee004d1e1936/original.png?1689092690


-------------
Spacing: 40px
-------------


**Headline**
SECTION RIGHT AND LEFT PADDING: 24px
PARAGRAPHS SPACING: null
IS HYPERLINKED: false
destination url: null
font-family: 'AkkuratLL', 'Public Sans', Arial, sans-serif;
font-size: 48px;
line-height: 68px;
color: #101926;
text-align: center;
font-weight: normal;
mso-line-height-rule: exactly;

-------------
Spacing: 24px
-------------


**Hero Image**
- Dimensions: 552x552
- SECTION RIGHT AND LEFT PADDING: 24px
- element type: gif
- make responsive: yes
- Alignment: center
- destination url: "#"
- source: https://braze-images.com/appboy/communication/assets/image_assets/images/695d127e3c66ea3ed6fc3c72/original.gif?1767707261



-------------
Spacing: 44px
-------------

**Body copy**
SECTION RIGHT AND LEFT PADDING: 48px
PARAGRAPHS SPACING: null
IS HYPERLINKED: false
destination url: null
font-family: 'AkkuratLL', 'Public Sans', Arial, sans-serif;
font-size: 24px;
line-height: 28px;
color: #000000;
text-align: center;
font-weight: normal;
mso-line-height-rule: exactly;

-------------
Spacing: 32px
-------------

**Button**
SECTION RIGHT AND LEFT PADDING: 24px
BUTTON ALIGNMENT: CENTER
destination url: #
border-radius: 32px;
font-family: 'AkkuratLL', 'Public Sans', Arial, sans-serif;
font-size: 16px;
line-height: 20px;
mso-padding-alt: 12px 24px;
color: #FFFFFF;
font-weight: normal;
display: block;
text-decoration: none;
background-color: #19191c;
text-align: center;
mso-line-height-rule: exactly;
padding: 12px 24px;

-------------
Spacing: 15px
-------------