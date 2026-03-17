<!-- The workflow details a simple web app that allows an professional HTML email developer to train an AI model on how they write email code and then generate the HTML code for a new email design -->

# Stage 1 - Learn the email design system of the HTML

**steps**

1. Extract the following information from the email's HTML code:
   - the colours, background colours, font sizes, line heights, letter spacings, and font families and their import formats (e.g. Google Fonts, Adobe Fonts, etc.)
   - the framework/library/templating language used (e.g. MJML, Marketo, HubSpot, plain HTML, etc.)
   - the components used (e.g. buttons, images, text blocks, etc.)
   - the layout structure (e.g. rows, columns, etc.)

2. Generate a draft design system that includes all the extracted information and present it to the email developer.

3. The email developer will then fine-tune the draft design system to ensure that it accurately reflects their design system, brand specifications, and coding style and syntax.

4. Save the final design system as a vector embedding in a vector database in such a way that it can easily be queried when analysing a future email design or generating the code for the new email.


# Stage 2 - Embed the HTML email

**steps**

- Get each individual section
- Convert every single detail/ visual property of each section into natural language.
- Take a screenshot of each section and save it as an image file.
- The following should then be stored as a vector embedding in a vector database for each section:
  - its natural language description
  - its screenshot
  - its UID

# Stage 3 - Stage and preprocess the email design

**steps**

- User uploads the design of the new email in image format (e.g. PNG, JPEG, etc.)
- The uploaded design is then divided into sections, using the stored vector embeddings as a reference to correctly identify the boundaries of each section.
- Each section is then preprocessed to extract its visual properties and convert them into a natural language description, which will be used in the next stage to generate the HTML code.

# Stage 4 - Convert the new email design into HTML code

**steps**

- Use the stored vector embeddings to generate the email's HTML code by:
  - Performing a similarity search in the vector database to find the most relevant sections based on the natural language descriptions and screenshots for each new section of the new email design. (done synchonously for each section to save time and context window limits)
  - Using the HTML code of the retrieved sections as a base for generating the new HTML code for each section of the new email design, keeping the code structure and syntax consistent with the email developer's coding style and design system, and only updating it to match the visual properties of the new email design.
  - Performing a self correction loop by taking a screenshot of the generated HTML code for each section and comparing it with its corresponding section in the new email design, and if there are any discrepancies, note them and use them to update the generated HTML code accordingly until it matches the new email design exactly.
  - Mapping each generated section of the HTML code to the sources in the vector database that were used to generate it, so that the email developer can easily trace back the source of each section of the generated HTML code and make any necessary adjustments or corrections based on the original design system and coding style.
  - Assembling the generated HTML code for each section into a complete email template.
