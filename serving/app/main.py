# Code by omoknooni
# Tensorflow Serving API

from flask import Flask, render_template, request, Response
from werkzeug.utils import secure_filename
from google.cloud import storage
from PIL import Image, ImageOps

import os
import io
import json
import uuid, traceback
import requests
import numpy as np

app = Flask(__name__)
app.config['UPLOAD_DIR'] = '/tmp/'
TENSOR_URL = 'http://[internal docker network ip]:8501/v1/models/wowboard:predict'

ALLOWED_CONTENT_TYPE = {
    'jpg':'image/jpeg',
    'jpeg':'image/jpeg',
    'png':'image/png',
}
ALLOWED_EXTENSION = sorted(ALLOWED_CONTENT_TYPE.keys())

BUCKET_NAME = 'wowbd-detected-img'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/app/[gcp storage iam account json file]'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSION

def prepare_image(image, target):
    if image.mode != "RGB":
        image = image.convert("RGB")
    image = image.resize(target)
    image = np.array(image, dtype=np.uint8)
    return image


@app.route('/')
def home():
   return Response(json.dumps({'status': 'healthy'}), mimetype='application/json', status=200)

# @app.route('/upload_test')
# def upload_test():
#     return render_template('upload_test.html')

@app.route('/upload', methods=['POST'])
def upload():
    if request.method == "POST":
        file_obj = request.files['file']
        TEMP_FILENAME = os.path.join(app.config['UPLOAD_DIR'],secure_filename(file_obj.filename))
        task_id = str(uuid.uuid4())
        dest_name = task_id + os.path.splitext(file_obj.filename)[1]
        file_obj.save(os.path.join(TEMP_FILENAME))

        storage_client = storage.Client()
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(task_id + '/' + dest_name)
        blob.upload_from_filename(TEMP_FILENAME)
        print(f'File {TEMP_FILENAME} uploaded to {dest_name}')

        try:
            # preprocessing
            with open(TEMP_FILENAME, 'rb') as f:
                img_data = f.read()
            image = Image.open(io.BytesIO(img_data))
            image = ImageOps.exif_transpose(image)
            image = prepare_image(image, target=(1024,1024)) 
            height, width, _ = image.shape
            origin_image = image.copy()

            # add axis
            image = image[np.newaxis, :, :]

            # detection
            image_data = json.dumps({"signature_name": "serving_default", "instances": image.tolist()})
            res = requests.post(TENSOR_URL, data=image_data)

            # extract Result
            result = res.json()["predictions"][0]
            num_detections = int(result["num_detections"])

            result['detection_scores'] = np.array(result["detection_scores"], dtype=np.float32)
            result['detection_boxes'] = np.array(result["detection_boxes"], dtype=np.float32)

            obj_index = result['detection_scores'] > 0.65
            score = result["detection_scores"][obj_index]     # 0.973602414
            boxes = result["detection_boxes"][obj_index]      # [0.302173734, 0.617861152, 0.531666338, 0.770464897]
            num_detections = obj_index.tolist().count(True)

            for idx, obj in enumerate(boxes):
                obj_image = origin_image[int(obj[0]*height):int(obj[2]*height),int(obj[1]*width):int(obj[3]*width)].copy()
                obj_save = Image.fromarray(obj_image)
                obj_local = os.path.join(app.config['UPLOAD_DIR'], f'obj_{idx}.png')
                obj_save.save(obj_local)

                #TODO : extension
                obj_blob = bucket.blob(task_id + '/' + f'obj_{idx}.png')
                obj_blob.upload_from_filename(obj_local)

            
        except Exception as e:
            print(traceback.print_exc())
            if res.json:
                return Response(json.dumps({'Error' : 'detection failed', 'traceback': str(res.json())[:50]}), mimetype='application/json', status=500)
        
        if num_detections:
            return Response(json.dumps({'status': 'success', 'task_id': task_id, 'num_detections': num_detections,'score': score.tolist(), 'boxes': boxes.tolist()}), mimetype='application/json', status=200)
        else:
            return Response(json.dumps({'status': 'success', 'task_id': task_id}), mimetype='application/json', status=200)
    else:
        return Response(json.dumps({'Error':'Method not allowed'}), mimetype='application/json', status=405)


if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host='0.0.0.0', debug=True, port=80)
