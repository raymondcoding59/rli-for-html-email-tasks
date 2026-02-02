import cv2 as cv
import numpy as np
from pathlib import Path
import time


# Define the base directory
BASE_DIR = Path(__file__).resolve().parent

# Start timer and show running message
start_time = time.time()
print("running...")


# Load and display the original design image
original_design = cv.imread(BASE_DIR / "design.png")
# cv.imshow('Original Design', original_design)





# write text on the design
text_on_design = original_design.copy()
cv.putText(text_on_design, "Hello World!", (text_on_design.shape[1]//3, 100), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
cv.imwrite(BASE_DIR / "layouts/01_text_on_design.png", text_on_design)




#draw shapes on the design
shapes_on_design = original_design.copy()
# rectangle
cv.rectangle(shapes_on_design, ((shapes_on_design.shape[1]//2)-50, (shapes_on_design.shape[0]//2)-50), (shapes_on_design.shape[1]//2+50, shapes_on_design.shape[0]//2+50), (255, 0, 0), cv.FILLED)  
# circle
cv.circle(shapes_on_design, (shapes_on_design.shape[1]//2, shapes_on_design.shape[0]//2), shapes_on_design.shape[1]//2, (0, 255, 255), 1)  
# line
cv.line(shapes_on_design, (0, 0), (shapes_on_design.shape[1], shapes_on_design.shape[0]), (255, 255, 255), 1)  

cv.imwrite(BASE_DIR / "layouts/02_shapes_on_design.png", shapes_on_design)



#paint the image a certain design
painted_design = original_design.copy()
painted_design[:] = 0, 255, 0 
cv.imwrite(BASE_DIR / "layouts/03_painted_design.png", painted_design)



# highlight horizontal spaces in red and save the design
highlighted_design = original_design.copy()
for row in range(highlighted_design.shape[0]):
    if all(highlighted_design[row, col][0] == highlighted_design[row, 0][0] and
           highlighted_design[row, col][1] == highlighted_design[row, 0][1] and
           highlighted_design[row, col][2] == highlighted_design[row, 0][2]
           for col in range(highlighted_design.shape[1])):
        for col in range(highlighted_design.shape[1]):
            highlighted_design[row, col] = [0, 0, 255]  # BGR format for red color
cv.imwrite(BASE_DIR / "layouts/04_highlighted_spaces.png", highlighted_design)


# convert the design to grayscale
grayscale_design = cv.cvtColor(original_design, cv.COLOR_BGR2GRAY)
cv.imwrite(BASE_DIR / "layouts/05_grayscale_design.png", grayscale_design)



# blur the design using Gaussian blur
blurred_design = cv.GaussianBlur(original_design, (15, 15), 0)
cv.imwrite(BASE_DIR / "layouts/06_blurred_design.png", blurred_design)



# detect edges in the design using Canny edge detection
edges_in_design = cv.Canny(original_design, 100, 200)
cv.imwrite(BASE_DIR / "layouts/07_edges_in_design.png", edges_in_design)



# resize the design to half its size
resized_design = cv.resize(original_design, (original_design.shape[1]//2, original_design.shape[0]//2))
cv.imwrite(BASE_DIR / "layouts/08_resized_design.png", resized_design)

#crop a portion of the design
cropped_design = original_design[200:400, 200:400]
cv.imwrite(BASE_DIR / "layouts/09_cropped_design.png", cropped_design)

# End timer and show done message
end_time = time.time()
print("done in", round(end_time - start_time, 2), "seconds")
cv.waitKey(0)