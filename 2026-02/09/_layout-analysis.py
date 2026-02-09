import cv2 as cv
import numpy as np
from pathlib import Path
import time
import json

# Define the base directory
BASE_DIR = Path(__file__).resolve().parent

# Start timer and show running message
start_time = time.time()
print("running...")


# Load and display the original design image
original_design_bgr = cv.imread(str(BASE_DIR / "design.png"))
# cv.imshow('Original Design', original_design)

#convert BGR to RGB
original_design = cv.cvtColor(original_design_bgr, cv.COLOR_BGR2RGB)

# save origianl design as a text file
with open(str(BASE_DIR / "design.txt"), "w") as f:
    for row in original_design:
        for pixel in row:
            f.write(f"{pixel[0]},{pixel[1]},{pixel[2]} ")
        f.write("\n")
        
# render the design from the text file
rendered_design = []
with open(str(BASE_DIR / "design.txt"), "r") as f:
    for line in f:
        row = []
        for pixel_str in line.strip().split():
            r, g, b = map(int, pixel_str.split(","))
            row.append([r, g, b])
        rendered_design.append(row)
rendered_design = np.array(rendered_design, dtype=np.uint8)

cv.imshow('Rendered Design', rendered_design)

# highlight horizontal spaces in red and save the design
highlighted_design = original_design.copy()
for row in range(highlighted_design.shape[0]):
    if all(highlighted_design[row, col][0] == highlighted_design[row, 0][0] and
           highlighted_design[row, col][1] == highlighted_design[row, 0][1] and
           highlighted_design[row, col][2] == highlighted_design[row, 0][2]
           for col in range(highlighted_design.shape[1])):
        for col in range(highlighted_design.shape[1]):
            highlighted_design[row, col] = [0, 0, 255]  # BGR format for red color
cv.imwrite(str(BASE_DIR / "layouts/04_highlighted_spaces.png"), highlighted_design)



# determine the hex background colour of the email
hex_background_color = '#{:02x}{:02x}{:02x}'.format(original_design[0,0,2], original_design[0,0,1], original_design[0,0,0])
print("Hex Background Color:", hex_background_color)

#determine if the background of the email is included in the image input


# determine the width of the email apart from the background spaces
content_width = 0
for col in range(original_design.shape[1]):
    if not all(original_design[row, col][0] == original_design[0, 0][0] and
               original_design[row, col][1] == original_design[0, 0][1] and
               original_design[row, col][2] == original_design[0, 0][2]
               for row in range(original_design.shape[0])):
        content_width += 1

print("Content Width:", content_width)

#determine the height of the padding at the top of the email befor the content starts
top_padding_height = 0
for row in range(original_design.shape[0]):
    if all(original_design[row, col][0] == original_design[0, 0][0] and
           original_design[row, col][1] == original_design[0, 0][1] and
           original_design[row, col][2] == original_design[0, 0][2]
           for col in range(original_design.shape[1])):
        top_padding_height += 1
    else:
        break

print("Top Padding Height:", top_padding_height)



# put the results in a dictionary and save as json
# results = {
#     "hex_background_color": hex_background_color,
#     "content_width": content_width,
#     "top_padding_height": top_padding_height
# }
# with open(str(BASE_DIR / "specifications.json"), "w") as f:
#     json.dump(results, f, indent=4)
    




# End timer and show done message
end_time = time.time()
print("done in", round(end_time - start_time, 2), "seconds")
cv.waitKey(0)