import cv2
import numpy as np
import glob
import os
import imgaug.augmenters as iaa

folder_path = '~/original/'
save_path = '~/augmented/'

aug = iaa.Sequential([
    iaa.ChangeColorTemperature((3700, 9000))  #적절한 값 찾기/ 3000대: 푸른색
])

for img_path in glob.glob(os.path.join(folder_path, "*.png")):
    img = cv2.imread(img_path)
    image_aug = aug.augment_images([img])

    filename = os.path.splitext(os.path.basename(img_path))[0]
    new_filename = filename + "_aug" + ".png"
    cv2.imwrite(os.path.join(save_path, new_filename), image_aug[0])