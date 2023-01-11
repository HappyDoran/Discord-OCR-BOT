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

file_path = "sample.json"

data = {}
data['users'] = []
data['users'].append({
    "title": "How to get stroage size",
    "url": "https://codechacha.com/ko/get-free-and-total-size-of-volumes-in-android/",
    "draft": "false"
})
data['users'].append({
    "title": "Android Q, Scoped Storage",
    "url": "https://codechacha.com/ko/android-q-scoped-storage/",
    "draft": "false"
})
print(data)

with open(file_path, 'w') as outfile:
    json.dump(data, outfile, indent="\t")
