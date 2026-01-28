# Prompt
Convert this email design into a pixel-perfect HTML email that is compatible with all email clients, mobile-responsive, and dark-mode friendly. 


Use the following instructions

## INSTRUCTIONS

### General
- Find the specifications of each element in the attached specifications.md, specifications for non-mentioned elements should be inferred from the design.
- When in doubt, or when the specification for any element is not clear or not defined at all, use the design as the ultimate source of truth.
- Do not ever default to: "best practices", "Industry standards", "Visual improvements", or similar approaches if they contradict the design or the specifications.

### Styles
- Use inline CSS as much as possible. Use the style tag for the other declarations such as fonts, responsive, and dark mode styles.

### Fonts
- Use the @import rule to import any mentioned web fonts.


### Spacing, Margins & Paddings
- Do not create a separate spacing element. Always use the "td tag" top-padding of the lower section/element to create the spacing between two sections/elements. For the first element/section in a pile, use its top-padding, and for the last element/section in a pile, use its top-padding and bottom-padding. For texts/copy always use the top-margin of the "p tag" containing each paragraph for spacing. Bottom-margin for each paragraph should always be 0, relying on the bottom-padding of the containing td tag if the text/copy is the last section in a pile.

- The generated HTML is invalid if there are any empty spacing elements.

- Do not apply the email's left and right padding to the email container, rather apply it to each section individually, in their outermost "td tag".

- Some Sections/elements like full-width images already have the right and left padding baked in, so confirm before applying padding.

### Images
- Use placehold.co image placeholders for all images and icons whose source urls are not specified(with .png image type, background colour as the inferred background of the image, and text color as the inferred text color of the image).
