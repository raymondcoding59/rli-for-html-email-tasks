I've updated the script to suite mu workspace. Now, keeping all else thesame, update the script to do the following:

- all intermediate generated resources like the extracted styles and layout should also be saved in the output_path
- Use the latest versions of gpt
- the returned outputs throughout should be plain, no ```html ``` fencing, no explanations 



The generated HTML does not even remotely match the structure or coding style of the reference-code neither does it resemble the target-generated-code. Analyse the code that gpt generated attached below as output.html, and update the script to ensure that:
- The generated code MUST match the coding convensions, formats, structure, styles etc of the reference code. The Ideal example of what the generated HTML should look like target-generated-code.html
- This script MUST be able to accomplish this for any email code reference and attached design pair too.
- placehold.co(with .png type) placeholder images should be used in place of assets (images, banners, logos, icons) that were not already learned frrom the reference code.



-----
- the script should always say(print) what process it is currently running, so I'm aware.

- A readme file should also be maintained in the output path contianing all the all the calls made to the open API, with the amount of input, output and total tokens used for each. There should also be a grand tatal of tokens used for the entire process