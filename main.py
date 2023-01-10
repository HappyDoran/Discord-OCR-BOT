# import pytesseract
# import cv2
# from difflib import SequenceMatcher
# import csv
#
#
#
# path = 'Photo/L3.png'
#
# image = cv2.imread(path)
#
# # h, w, c = image.shape
# # output = image[int(0.3 * h): int(0.53 * h), int(0.7 * w): int(0.92 * w)]
#
# rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#
# # cv2.imshow("output", output)
# # cv2.waitKey()
# # cv2.destroyAllWindows()
#
# # use Tesseract to OCR the image
#
# text = pytesseract.image_to_string(rgb_image, lang='kor+eng')
# # text = text.replace(" ", "")
# print(text)
#
# l = text.split('\n')
# l = list(filter(None,  l))
# print(l)
import csv

f = open('mapp.csv', 'r', encoding='UTF-8')
rdr = csv.reader(f)
for line in rdr:
    print(line[1])