I want to build a NextJS spa that:
1. povides a drag and drop/file picker input for the user to drop a html email file
2. Renders the HTML email file while awaiting the user to confirm that that's the file they want to use
3. After the file is confirmed, the HTML email gets sent to chatgpt using the openAI API, and asked to create a design system in markdown format, using the details found in html file.
4. After the html email code is processed by ChatGPT, the output is then displayed in the app in a fenced block as markdown.

Give me 
1. The overall structure of how the project should be set up using the app router. Also use a file tree to demonstrate this
2. Every tip I would need for the app to run efficiently and securely.
3. The Nextjs code for the app