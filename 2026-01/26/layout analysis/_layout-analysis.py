import cv2 as cv
from pathlib import Path


# Define the base directory
BASE_DIR = Path(__file__).resolve().parent.parent



# Load and display the original design image
original_design = cv.imread(BASE_DIR / "design.png")
cv.imshow('Original Design', original_design)



# cv.imwrite(BASE_DIR / "layout-analysis/original_design.png", original_design)



cv.waitKey(0)