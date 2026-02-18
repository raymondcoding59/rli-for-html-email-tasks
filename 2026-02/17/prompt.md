
# 1
You are a senior email designer and developer. You have been given an email design to analyse and create specifications for. Your task is to break down the email design into its individual elements, such as images, text/copy, buttons, icons, etc., and create detailed specifications for each element. Your first step is to create a comprehensive list of all the elements in the email design, ordered by how they would be arranged in a table-based HTML code, i.e. row-by-row, top-to-bottom. In your output, the list of elements should be in a detailed and well-structured fenced Markdown code block, other parts of the output can be in normal output.

Use the following guidelines to create the row-by-row list of elements:
- Before you list any elements/rows, ensure that they follow the exact order that they appear in the design. This is a must! Left-to-right, top-to-bottom. 

- This list of rows and elements is simply meant to be a record/source of truth for what is included in the email design, and is not meant to be a list of specifications. The specifications will be created in the next step, where you will use this list as a reference to create detailed specifications for each element. when listing the elements, be discriptive as least as possible in terms of the visual details of the elements, such as colors, fonts, sizes, alignments, spacings, etc., stating only the bare minimum that can be used to identify the element in the design.

- Only include rows and elements that are visible in the design. If an element is not visible, it should not be included in the list. Auxiliary elements that are not visible in the design, such as padding or spacing elements, should also be excluded from the list.

- Some rows might be intended to be solid images, such as hero or banner images. Your determining factor for deciding that a row is a solid image(when not obviously a banner or hero image) should be if you have a clear and bulletproof structure of how you'll implement the row and its elements in HTML using the table-based approach. If you don't have a clear structure for implementing the row, then it's likely that the row is a solid image and should be treated as such.

Also, if the implementation of a row is not clear due to the complexity of the design and layout (e.g., overlapping elements, intricate/complicated typography, decorative graphics, over-reliance on VML or no clear way to make the row mobile responsive), then it should simply be treated as a solid image.


- The list should have a label, i.e. "row 1", followed by a one-sentence description of each of the elements in that row, if it's not a solid image. 

- Ensure that the list is exhaustive and includes every single element(including horizontal rules) in the email design, without missing any details. This will help ensure that the specifications you create later are accurate and comprehensive.

- Blocks of text that contain more than one paragraph should not be broken into different rows, but should be listed in one row and noted as having multiple paragraphs.


- Some types of elements/rows should ideally be grouped together in one parent row, these include:

  - Lists and bullet points, including their intro and outro(if applicable)
  - A group of elements in a particular section that share the same background color, background image or bounded by a container/border.
  
  These should be considered as rows of one parent row, and would technically be implemented as a single table row with multiple nested tables for the inner rows and elements. The parent row should be noted as such, and the inner rows should be listed as sub-rows under the parent row, with their corresponding elements listed under each sub-row. 
  
  IMPORTANT: Except for when a section(group of consecutive row/elements, which together, form a distinct part of the email) is bounded by a container, border or background, nesting of rows should be used sparingly, applied judiciously to only a group of elements that are clearly part of the same section (quintessential example: a list with intro and outro text)

# 2

I've attached an email design, a prompt I gave chatGPT to list every single element in the email design by grouping them into rows based on how the'll be stuctured in a table based HTML email code, and a the list of elements provided by ChatGPT after the analysis.

Your Job is perform a thorough comparism between the original design and the provided list of elements and ensure it meets all the criteria in the prompt.

