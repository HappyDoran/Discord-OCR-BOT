import pytesseract
import cv2
from difflib import SequenceMatcher
import csv



path = 'Photo/5b80a0cb-cdc7-4cd6-af13-7a55f9d4ea2e.jpg'

image = cv2.imread(path)

h, w, c = image.shape
output = image[int(0.3 * h): int(0.53 * h), int(0.7 * w): int(0.92 * w)]

rgb_image = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)

# cv2.imshow("output", output)
# cv2.waitKey()
# cv2.destroyAllWindows()

# use Tesseract to OCR the image

text = pytesseract.image_to_string(rgb_image, lang='kor')
print(text)