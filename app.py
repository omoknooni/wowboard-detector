from flask import Flask, render_template, request, Response
from werkzeug import secure_filename
from PIL import Image

import json
import os
import numpy as np
import tensorflow as tf

from object_detection.utils import ops as utils_ops
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util
# from detection import show_inference

app = Flask(__name__)
UPLOAD_PATH = '/<PATH>/<TO>/<IMAGE>'
MODEL_PATH = '/<PATH>/<TO>/<MODEL>'
LABELMAP_PATH = '/<PATH>/<TO>/<LABELMAP>'
OUTPUT_PATH = '/<PATH>/<TO>/<OUTPUT>'

category_index = label_map_util.create_category_index_from_labelmap(LABELMAP_PATH, use_display_name=True)

ALLOWED_CONTENT_TYPE = {
    'jpg':'image/jpeg',
    'jpeg':'image/jpeg',
    'png':'image/png',
}
ALLOWED_EXTENSION = sorted(ALLOWED_CONTENT_TYPE.keys())

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSION

def show_inference(model, image_path):
  # the array based representation of the image will be used later in order to prepare the
  # result image with boxes and labels on it.
  image_np = np.array(Image.open(image_path))
  temp_image = image_np.copy()
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
    result_img.save(os.path.join(OUTPUT_PATH,filename))
    print(f'[*] {filename} saved to {OUTPUT_PATH}')
  except Exception as e:
    print(f'[!] Saving failed... : {e}')

def run_inference_for_single_image(model, image):
  image = np.asarray(image)
  # The input needs to be a tensor, convert it using `tf.convert_to_tensor`.
  input_tensor = tf.convert_to_tensor(image)
  # The model expects a batch of images, so add an axis with `tf.newaxis`.
  input_tensor = input_tensor[tf.newaxis,...]

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
  height, width, _ = img.shape

  # TODO : detection_score가 몇 점 이상일때 객체 cropping을 해올 것인가?
  # 너무 낮은 경우 오탐이 많아지고, 너무 높은 경우 인식된 객체의 수가 줄어들 것이다
  obj_index = output_dict['detection_scores'] > 0.9
  scores = output_dict['detection_scores'][obj_index]
  boxes = output_dict['detection_boxes'][obj_index]
  classes = output_dict['detection_classes'][obj_index]

  for i in range(len(boxes)):
    coord = [boxes[i][0],boxes[i][1],boxes[i][2],boxes[i][3]]
    object_list.append(coord)
    # print(f'>> {i} : ({coord})')

  object_list.sort(key=lambda x:x[1])
  # print(f'Total : {object_list}')

  for idx, obj in enumerate(object_list):
    obj_img = img[int(obj[0] * height):int(obj[2] * height), int(obj[1] * width):int(obj[3] * width)].copy()
    obj_save = Image.fromarray(obj_img)

    name, ext = os.path.splitext(filename)
    path = os.path.join(OUTPUT_PATH,name+f'_{idx+1}'+ext)
    obj_save.save(path)
    print(f'>>> Detected object #{idx+1} has been saved as {path}')


@app.route('/detect', method=['POST'])
def analyze():
    if request.method == "POST":
        input_img = request.files['data']
        if input_img and allowed_file(input_img.filename):
            filename = secure_filename(input_img.filename)

            save_path = os.path.join(UPLOAD_PATH,filename)
            input_img.save(save_path)

            # Detecting
            show_inference(MODEL_PATH, save_path)
    else:
        return Response({'Error':'Method not allowed'}, status=405)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)