import cv2 as cv
from pathlib import Path


# Define the base directory
BASE_DIR = Path(__file__).resolve().parent.parent

print("running...")


# Load and display the original design image
original_design = cv.imread(BASE_DIR / "design.png")
# cv.imshow('Original Design', original_design)

# highlight spaces in red
for row in range(original_design.shape[0]):
    if all(original_design[row, col][0] == original_design[row, 0][0] and
           original_design[row, col][1] == original_design[row, 0][1] and
           original_design[row, col][2] == original_design[row, 0][2]
           for col in range(original_design.shape[1])):
        for col in range(original_design.shape[1]):
            original_design[row, col] = [0, 0, 255]  # BGR format for red color
cv.imwrite(BASE_DIR / "layout-analysis/highlighted_spaces.png", original_design)

# cv.imwrite(BASE_DIR / "layout-analysis/original_design.png", original_design)



cv.waitKey(0)