**1**
---
You are a senior email designer and developer. You have been given an email design to analyse and create specifications for. Your task is to break down the email design into its individual elements, such as images, text/copy, buttons, icons, etc., and create detailed specifications for each element. Your first step is to create a comprehensive list of all the elements in the email design, ordered by how they would be arranged in a table-based HTML code, i.e. row-by-row, top-to-bottom. In your output, the list of elements should be in a detailed and well-structured fenced Markdown code block, other parts of the output can be in normal output.

Use the following guidelines to create the row-by-row list of elements:

- Only include rows and elements that are visible in the design. If an element is not visible, it should not be included in the list.
- Some rows might be intended to be solid images, such as hero or banner images. Your determining factor for deciding that a row is a solid image(when not obviously a banner or hero image) should be if you have a clear and bulletproof structure of how you'll implement the row and its elements in HTML using the table-based approach. If you don't have a clear structure for implementing the row, then it's likely that the row is a solid image and should be treated as such.

Also, if the implementation of a row is not clear due to the complexity of the design and layout (e.g., overlapping elements, intricate/complicated typography, decorative graphics, over-reliance on VML or no clear way to make the row mobile responsive), then it should simply be treated as a solid image.

- The list should have a label, i.e. "row 1", followed by a one-sentence description of each of the elements in that row, if it's not a solid image. 

- Ensure that the list is exhaustive and includes every single element(including horizontal rules) in the email design, without missing any details. This will help ensure that the specifications you create later are accurate and comprehensive.


**2**
---
Give me a list of every element in this email design. The elements should be ordered by how they would be arranged in a table-based HTML code, i.e. row-by-row, top-to-bottom. Your output should be in a markdown file format.

Take special consideration for the following elements:\

***images***
- Images may sometimes contain text, especially hero and banner images. In such cases, the text inside the image should not be considered as a separate text element, rather it should be considered as part of the image element itself.

***text/copy***
- Short texts or whole copy sections might contain parts with different stylings, such as bold, italic, colored, or hyperlinked text. In such cases, the differently styled parts should be noted as well and all their visible differences in styling should be noted in the specifications of the text/copy element.\
If a text/copy element contains what you strongly believe to be a link, then it should be noted as such, along with its visible styling differences from the rest of the text/copy.


**3**
---
Generate an exhaustive JSON document of specifications for every single element in this email design so that a third party would be able to recreate this email in HTML without seeing the original design.

A list of elements in the email design is provided in 01_elements.md. The elements should be grouped in rows by how they appear in the design and how they would be arranged row by row in a table-based HTML format. Find the specifications formats for various element types in specification-guide.json, use placehold.co for URLs of images and Icons(with .png file type)


