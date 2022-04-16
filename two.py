#!/usr/bin/env python
# coding: utf-8

import io
import fitz
import numpy as np
from PIL import Image, ImageOps, ImageFilter, ImageEnhance
import pytesseract
import pandas as pd

zoom = 4
mat = fitz.Matrix(zoom, zoom)
config = r'--oem 3 --psm 12 -c tessedit_char_whitelist=0123456789,%'


def prepare(image):
    image = image.convert('L')
    image = image.filter(ImageFilter.SMOOTH_MORE)
    image = ImageOps.invert(image)
    brightness = ImageEnhance.Brightness(image)
    image = brightness.enhance(1.2)
    return image


values = []


def read2(file, pageNumber):
    global values
    pdf = fitz.open(file)
    page = pdf.load_page(pageNumber)
    pixmap = page.get_pixmap(alpha=False, matrix=mat).tobytes()
    image = Image.open(io.BytesIO(pixmap))
    invert_im = image.convert("RGB")
    invert_im = ImageOps.invert(invert_im)
    imageBox = invert_im.getbbox()
    cropped = image.crop(imageBox)
    aspect_ratio = cropped.height / cropped.width
    new_width = 2121
    new_height = int(new_width * aspect_ratio)
    resized = cropped.resize((new_width, new_height), Image.NEAREST)
    #print('width:', resized.width, 'height:', resized.height)
    image_arr = np.array(resized)
    image_arr = image_arr[730:image.height*2, 1500:1900]
    image = Image.fromarray(image_arr)
    im2 = prepare(image)

    results = pytesseract.image_to_string(im2, config=config)
    a_list = results.split('\n')
    out = [i for i in a_list if i]
    out.remove('\x0c')
    out = [value.replace(',', '.').replace('%', '') for value in out]
    out = out[:-2]
    for index, value in enumerate(out):
        if len(value) != 5:
            print('ALERT!!!', index, value)
    it = iter(out)
    data = list(zip(it, it))
    for tuple_ in data:
        values.append(tuple_)
        #print(tuple_[0], '-', tuple_[1])
    # im2.show()


for i in range(0, 9):
    read2('./data/report.pdf', i)

df = pd.DataFrame(values, columns=['prima_dose', 'seconda_dose'])
df.to_csv('out.csv')

print(len(values))
