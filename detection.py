# Code by omoknooni
# Tensorflow Object Detection API Detection


import numpy as np
import os
import pathlib
import six.moves.urllib as urllib
import sys
import tarfile
import tensorflow as tf
import zipfile
import copy

from collections import defaultdict
from io import StringIO
from matplotlib import pyplot as plt
from PIL import Image, ImageOps
from IPython.display import display

from object_detection.utils import ops as utils_ops
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

# argument parse
flags = tf.compat.v1.flags
flags.DEFINE_string('image_dir', '', 'Path to images')
flags.DEFINE_string('output_dir', '', 'Path to output where detection result stores')
flags.DEFINE_string('detection_model', '', 'Path to detection model')
flags.DEFINE_string('label_map_dir','', 'Path to label map')
FLAGS = flags.FLAGS

# load detection model
detection_model = tf.saved_model.load(FLAGS.detection_model)

# load image_dir, label map
PATH_TO_IMAGES_DIR = pathlib.Path(FLAGS.image_dir)
PATH_TO_LABELS = FLAGS.label_map_dir
category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)
# detection할 이미지는 jpg로 고정
IMAGE_PATH = sorted(list(PATH_TO_IMAGES_DIR.glob('*.png'))+list(PATH_TO_IMAGES_DIR.glob('*.jpg')))

def show_inference(model, image_path):
  # the array based representation of the image will be used later in order to prepare the
  # result image with boxes and labels on it.
  image = Image.open(image_path)
  image = ImageOps.exif_transpose(image)
  image_np = np.array(image)
  temp_image = image_np.copy()
  # print(f'[1] temp_image : {temp_image.shape}')
  filename = image_path.name
  
  # Actual detection.
  print(f'[*] Detection from {filename}...')
  output_dict = run_inference_for_single_image(model, image_np)
  # Visualization of the results of a detection.
  vis_util.visualize_boxes_and_labels_on_image_array(
      image_np,
      output_dict['detection_boxes'],
      output_dict['detection_classes'],
      output_dict['detection_scores'],
      category_index,
      instance_masks=output_dict.get('detection_masks_reframed', None),
      use_normalized_coordinates=True,
      line_thickness=8)

  # display(Image.fromarray(image_np))
  result_img = Image.fromarray(image_np)

  cropping_entities(temp_image, output_dict, filename)

  try:
    result_img.save(os.path.join(FLAGS.output_dir,filename))
    print(f'[*] {filename} saved to {FLAGS.output_dir}')
  except Exception as e:
    print(f'[!] Saving failed... : {e}')

def run_inference_for_single_image(model, image):
  image = np.asarray(image)
  # print(f'[2] np.asarray : {image[:10]}')
  # The input needs to be a tensor, convert it using `tf.convert_to_tensor`.
  input_tensor = tf.convert_to_tensor(image)
  # print(f'[3] tf.convert_to_tensor : {input_tensor.shape}')
  # The model expects a batch of images, so add an axis with `tf.newaxis`.
  input_tensor = input_tensor[tf.newaxis,...]
  # print(f'[4] tf.newaxis : {input_tensor.shape}')

  # Run inference
  model_fn = model.signatures['serving_default']
  output_dict = model_fn(input_tensor)

  # All outputs are batches tensors.
  # Convert to numpy arrays, and take index [0] to remove the batch dimension.
  # We're only interested in the first num_detections.
  num_detections = int(output_dict.pop('num_detections'))
  output_dict = {key:value[0, :num_detections].numpy() 
                 for key,value in output_dict.items()}
  output_dict['num_detections'] = num_detections

  # detection_classes should be ints.
  output_dict['detection_classes'] = output_dict['detection_classes'].astype(np.int64)
   
  # Handle models with masks:
  if 'detection_masks' in output_dict:
    # Reframe the the bbox mask to the image size.
    detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
              output_dict['detection_masks'], output_dict['detection_boxes'],
               image.shape[0], image.shape[1])      
    detection_masks_reframed = tf.cast(detection_masks_reframed > 0.5,
                                       tf.uint8)
    output_dict['detection_masks_reframed'] = detection_masks_reframed.numpy()
    
  return output_dict

# 인식된 부분만을 cropping
def cropping_entities(img, output_dict, filename):
  object_list = []
  coord = []
  height, width, _ = img.shape

  # TODO : detection_score가 몇 점 이상일때 객체 cropping을 해올 것인가?
  # 너무 낮은 경우 오탐이 많아지고, 너무 높은 경우 인식된 객체의 수가 줄어들 것이다
  obj_index = output_dict['detection_scores'] > 0.65
  scores = output_dict['detection_scores'][obj_index]
  boxes = output_dict['detection_boxes'][obj_index]
  classes = output_dict['detection_classes'][obj_index]

  for i in range(len(boxes)):
    object_list.append([boxes[i][0],boxes[i][1],boxes[i][2],boxes[i][3]])
    # print(f'>> {i} : ({coord})')

  object_list.sort(key=lambda x:x[1])
  # print(f'Total : {object_list}')

  for idx, obj in enumerate(object_list):
    obj_img = img[int(obj[0] * height):int(obj[2] * height), int(obj[1] * width):int(obj[3] * width)].copy()
    obj_save = Image.fromarray(obj_img)

    xy_position = [int(obj[0] * height),int(obj[2] * height), int(obj[1] * width),int(obj[3] * width)]
    center_position = tuple([int((xy_position[0]+xy_position[1]) / 2), int((xy_position[2]+xy_position[3]) / 2)])
    print(f'position : {xy_position} || middle position : {center_position}')
    coord.append(center_position)

    name, ext = os.path.splitext(filename)
    path = os.path.join(FLAGS.output_dir,name+f'_{idx+1}'+ext)
    obj_save.save(path)
    print(f'>>> Detected object #{idx+1} has been saved as {path}')

  with open(os.path.join(FLAGS.output_dir, name+'_coord.txt'), 'w') as f:
    for line in coord:
      f.write(str(line) + '\n')
  f.close()

print(f'[*] {len(IMAGE_PATH)} files to Detection')

for image_path in IMAGE_PATH:
  show_inference(detection_model, image_path)