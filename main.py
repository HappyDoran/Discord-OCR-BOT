# import pytesseract
# import cv2
# from difflib import SequenceMatcher
# import csv
#
#
#
# path = 'Photo/another.png'
#
# image = cv2.imread(path)
#
# #h, w, c = image.shape
# #output = image[int(0.3 * h): int(0.53 * h), int(0.7 * w): int(0.92 * w)]
#
# rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#
# #cv2.imshow("output", rgb_image)
# #cv2.waitKey()
# #cv2.destroyAllWindows()
#
# # use Tesseract to OCR the image
# text = pytesseract.image_to_string(rgb_image, lang='kor')
# text = text.replace(" ", "")
# print(text)
#
# l = text.split('\n')
# l = list(filter(None,  l))
# print(l)

import json
from collections import OrderedDict
import pprint

file_path = 'User.json'

with open(file_path) as f:
    df = json.load(f)

print(df['{0}'.format(249356319616794627)])

df['{0}'.format(249356319616794628)] = {'nickname': '서동윈', 'point': 2}

print(df)

with open(file_path, 'w') as f:
    json.dump(df, f, indent=2, ensure_ascii=False)
