import pytesseract
import cv2
from difflib import SequenceMatcher




path = 'Photo/2a8e23af-3d28-419d-a932-7dd770f1f0f4.jpg'

image = cv2.imread(path)

h, w, c = image.shape
output = image[int(0.3068 * h): int(0.4999 * h), int(0.7099 * w): int(0.9475 * w)]

rgb_image = cv2.cvtColor(output, cv2.COLOR_BGR2RGB)

cv2.imshow("output", image)
#cv2.waitKey()
#cv2.destroyAllWindows()

# use Tesseract to OCR the image
text = pytesseract.image_to_string(rgb_image, lang='kor')
print(text)