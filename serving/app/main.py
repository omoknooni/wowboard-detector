from flask import Flask, render_template, request, Response
from werkzeug.utils import secure_filename
from google.cloud import storage
from PIL import Image

import os
import io
import json
import uuid, traceback
import requests
import numpy as np

app = Flask(__name__)
app.config['UPLOAD_DIR'] = '/tmp/'
TENSOR_URL = 'http://[internal docker network ip]:8501/v1/models/m1:predict'

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

        # TODO : upload시 바로 작업uuid folder 생성하고 그 안에 업로드
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
            image = prepare_image(image, target=(1024,1024)) 
            print(f'[1] image byte : {image[:20]}, image shape : {image.shape}')
            height, width, _ = image.shape 

            # add axis
            image = image[np.newaxis, :, :]

            # detection
            image_data = json.dumps({"signature_name": "serving_default", "instances": image.tolist()})
            res = requests.post(TENSOR_URL, data=image_data)
            print(res.json()["predictions"])

            # extract Result
            result = res.json()["predictions"]
            num_detections = int(result[0]["num_detections"])

            obj_list = []
            score = result[0]["detection_scores"][0:num_detections]     # 0.973602414
            boxes = result[0]["detection_boxes"][0:num_detections]      # [0.302173734, 0.617861152, 0.531666338, 0.770464897]

        except Exception as e:
            print(traceback.print_exc())
            if res.json:
                return Response(json.dumps({'Error' : 'detection failed', 'traceback':res.json()}), mimetype='application/json', status=500)
        
        if num_detections:
            return Response(json.dumps({'status': 'success', 'task_id': task_id, 'num_detections': num_detections,'score': score, 'boxes': boxes}), mimetype='application/json', status=200)
        else:
            return Response(json.dumps({'status': 'success', 'task_id': task_id}), mimetype='application/json', status=200)
    else:
        return Response(json.dumps({'Error':'Method not allowed'}), mimetype='application/json', status=405)

@app.route('/detect', methods=['POST'])
def analyze():
    if request.method == "POST":
        input_img = request.files['file']
        if input_img and allowed_file(input_img.filename):
            filename = secure_filename(input_img.filename)

            #save_path = os.path.join(UPLOAD_PATH,filename)
            #input_img.save(save_path)
            storage_client = storage.Client()
            bucket = storage_client.bucket(BUCKET_NAME)

            # Detecting
            res = request.post(TENSOR_URL, data={})
    else:
        return Response({'Error':'Method not allowed'}, status=405)

if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host='0.0.0.0', debug=True, port=80)
