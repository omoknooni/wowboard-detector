# tu11p

import os, sys
from PIL import Image

size = 1024, 1024  # cropped size
path = "~~/original/"  # original image path
modified_path = "~~/resized/"  # resized image path
os.chdir(path)


def resize_and_crop(img_path, modified_path, size, crop_type='middle'):     # middle crop
    files = os.listdir(img_path)

    for file in files:

        name, ext = os.path.splitext(file)      # extension split
        os.chdir(img_path)
        img = Image.open(file)
        img_ratio = img.size[0] / float(img.size[1])
        ratio = size[0] / float(size[1])

        if ratio > img_ratio:
            img = img.resize((size[0], int(round(size[0] * img.size[1] / img.size[0]))),
                             Image.ANTIALIAS)
            if crop_type == 'top':      # top/left crop
                box = (0, 0, img.size[0], size[1])
            elif crop_type == 'middle':
                box = (0, int(round((img.size[1] - size[1]) / 2)), img.size[0],
                       int(round((img.size[1] + size[1]) / 2)))
            elif crop_type == 'bottom':     # bottom/right crop
                box = (0, img.size[1] - size[1], img.size[0], img.size[1])
            else:
                raise ValueError('ERROR: invalid value for crop_type')
            img = img.crop(box)

        elif ratio < img_ratio:
            img = img.resize((int(round(size[1] * img.size[0] / img.size[1])), size[1]),
                             Image.ANTIALIAS)
            if crop_type == 'top':
                box = (0, 0, size[0], img.size[1])
            elif crop_type == 'middle':
                box = (int(round((img.size[0] - size[0]) / 2)), 0,
                       int(round((img.size[0] + size[0]) / 2)), img.size[1])
            elif crop_type == 'bottom':
                box = (img.size[0] - size[0], 0, img.size[0], img.size[1])
            else:
                raise ValueError('ERROR: invalid value for crop_type')
            img = img.crop(box)

        else:
            img = img.resize((size[0], size[1]), Image.ANTIALIAS)

        os.chdir(modified_path)
        img.save(name + '_resized' + '.png', 'png')


resize_and_crop(path, modified_path, size)