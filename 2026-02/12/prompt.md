**1**
---
Create a Markdown file containing every element in this email design



**2**
---
Generate an exhaustive JSON document of specifications for this email design so that a third party would be able to recreate this email in HTML without seeing the original design.

A list of elements in the email design are provided in elements.md. The JSON should follow thesame format in specification-guide.json, use placehold.co for URLs of images and Icons(with .png file type)




**3**
---
**Prompt**
Convert this email design into a pixel-perfect HTML email that is compatible with all email clients, mobile-responsive, and dark-mode friendly. 


Use the following instructions

**INSTRUCTIONS**

***General***
- Find the specifications of each element in the attached specifications.md, specifications for non-mentioned elements should be inferred from the design. A list of the elements in the email design are provided in elements.md, use it as a reference to identify the elements in the design.
- When in doubt, or when the specification for any element is not clear or not defined at all, use the design as the ultimate source of truth.
- Do not ever default to: "best practices", "Industry standards", "Visual improvements", or similar approaches if they contradict the design or the specifications.

***Styles***
- Use inline CSS as much as possible. Use the style tag for the other declarations such as fonts, responsive, and dark mode styles.

***Fonts***
- Use the @import rule to import any mentioned web fonts.


***Spacing, Margins & Paddings***
- Do not create a separate spacing element. Always use the "td tag" top-padding of the lower section/element to create the spacing between two sections/elements. For the first element/section in a pile, use its top-padding, and for the last element/section in a pile, use its top-padding and bottom-padding. For texts/copy always use the top-margin of the "p tag" containing each paragraph for spacing. Bottom-margin for each paragraph should always be 0, relying on the bottom-padding of the containing td tag if the text/copy is the last section in a pile.

- The generated HTML is invalid if there are any empty spacing elements.

- Do not apply the email's left and right padding to the email container, rather apply it to each section individually, in their outermost "td tag".
