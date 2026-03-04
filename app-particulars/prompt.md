I want to build a NextJS spa that:
1. povides a drag and drop/file picker input for the user to drop a html email file
2. Renders the HTML email file while awaiting the user to confirm that that's the file they want to use
3. After the file is confirmed, the HTML email gets sent to chatgpt using the openAI API, and asked to create a design system in markdown format, using the details found in html file.
4. After the html email code is processed by ChatGPT, the output is then displayed in the app in a fenced block as markdown.

Give me 
1. The overall structure of how the project should be set up using the app router. Also use a file tree to demonstrate this
2. Every tip I would need for the app to run efficiently and securely.
3. The Nextjs code for the app

Implement the following for :
**Security**
- input sanitation and validation to prevent malicious files from being processed.


**Over billing Protection**
- Client-side validation of file size and type before uploading to the server.
- Implement server-side validation to ensure that only allowed files and file sizes are processed.
- rate limiting to prevent abuse of the API and control costs.
- disable button after submission to prevent multiple requests, show a loading state to inform the user that their request is being processed.
- Abort duplicate requests

**User Experience**
- Provide clear instructions and feedback to the user throughout the process, such as confirming file upload, showing loading states, and displaying results in an easy-to-read format.
- Implement error handling to gracefully manage any issues that arise during file processing or API interactions, providing informative messages to the user.



Instead of the pages appearing after each stage is done, make them in for of tabs (left to right). The first tab will include the input box, render the HTML, and the confirm file and generate design system button(as one button). The next tab will render the design system markdown.

The tabs that the user has not gotten to yet will remail locked until the user has reached that stage, and the user should be able to go back to previous tabs at any stage in order to edit any details or reupload files and continue the process