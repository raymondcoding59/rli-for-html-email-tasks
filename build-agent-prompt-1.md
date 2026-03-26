I need to build an interactive web-based email developer assistant AI agent that'll work like so:
1. The email developer will upload a sample of their Ideal email code
2. The agent will break down the email code to learn the developer's coding, brand specifications of the email design, and structure of the code, i.e. 
    - Meta tags
        - fonts
        - Title
        - Outlook conditional tags 
    - Styles
        - fonts
        - Outlook specific styles 
        - media queries
    - preview text
    - Container structure
    - tracking pixels
    - Section structure(divs, tables, etc)
    - background images
    - VML
    - Responsive approach
    - multiple columns approach
    - elements structure
        - images
        - icons
        - text
        - buttons
        - links

3. A web interface will be provided for the developer to to confirm all of the above factors that the agent has identified in the email code, and to add any additional factors that the agent may have missed.
4. all of the above will be stored in a vector database in the best way possible for the AI to be able to reference it while generating the email code of a future email design.

5. The developer will then be able to ask the agent to generate email code for a new email design, and the agent will be able to reference the vector database to learn from the ideal email code sample that the developer uploaded, and generate new email code based on the factors that the developer confirmed.

