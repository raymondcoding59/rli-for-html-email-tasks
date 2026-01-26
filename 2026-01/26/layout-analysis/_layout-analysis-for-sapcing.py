import cv2 as cv
from pathlib import Path

print("running...")

# Define the base directory
BASE_DIR = Path(__file__).resolve().parent.parent



# Load and display the original design image
original_design = cv.imread(BASE_DIR / "design_spacing.png")
# cv.imshow('Original Design', original_design)

# calculate the number of pixels in the image
num_pixels = original_design.shape[0] * original_design.shape[1]
print(f"Number of pixels in the image: {num_pixels}")

# calculate the number of rows of pixels in the image
num_rows = original_design.shape[0]
print(f"Number of rows of pixels in the image: {num_rows}")


#calculate the number of rows of pixels that have just one color
num_single_color_rows = 0
for row in range(original_design.shape[0]):
    if all(original_design[row, col][0] == original_design[row, 0][0] and
           original_design[row, col][1] == original_design[row, 0][1] and
           original_design[row, col][2] == original_design[row, 0][2]
           for col in range(original_design.shape[1])):
        num_single_color_rows += 1

print(f"Number of rows of pixels with just one color: {num_single_color_rows}")

# make every single color row red and save the image as highlighted_spaces.png
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