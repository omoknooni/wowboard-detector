# wowboard-detector

## 라벨링 데이터 수집
라벨링한 데이터는 'stickynote_image'에 모두 저장한다. (이미지와 xml 모두)  
라벨링 인원 각각 branch를 파서 이미지 업로드, PR, 확인 후 main에 merge
## 개발환경
- Anaconda 22.9.0(Python 3.9.16)
- Tensorflow 2.10
- Protoc 22.0
- Visual Studio 2022


## 설치
[Tensorflow Object Detection API](https://github.com/tensorflow/models/tree/master/research/object_detection)를 git clone해 설치

[설치 Guide](https://omoknooni.tistory.com/46)

## 데이터 준비 및 학습
### 1. 데이터 수집
와우보드 위에 직접 포스트잇을 붙여서 촬영한 이미지와 단순히 포스트잇을 중심으로 한 이미지를 수집  
### 2. 데이터 라벨링
학습에 사용하기 위해 수집한 이미지 데이터를 라벨링하는 작업이 필요하다.  
LabelImg라는 오픈소스 툴을 이용해 작업을 진행한다.  

> [데이터 라벨링](./Labeling.md) 문서를 참고해 라벨링하기


PascalVOC dataset으로 설정 후 각 이미지를 라벨링, 라벨링된 이미지는 각각 xml파일이 생성된다

이미지데이터를 불러오고 오브젝트 영역(Bounding Box)을 지정, 학습데이터는 xml파일로 저장됨  
라벨링한 데이터셋은 학습(train)에 사용할 것과 평가확인(test)에 사용할 것으로 분리해준다.  
### 3. 단일 CSV파일 생성
각 이미지 별로 xml파일이 생성되었는데, 이를 하나의 csv파일로 묶어주어야 한다.  
토탈 2개의 csv가 생성, train용으로 분리한 데이터셋 과 test로 분리한 데이터셋
```bash
python xml_to_csv.py
```
### 4. Label Map 생성
인식할 객체의 정보를 담은 파일로 위의 데이터셋에서 라벨링했던 내용을 포함한다.  
id값은 1부터 시작하며, 저장할 파일의 확장자는 .pbtxt
```
item {
    id: 1
    name: "stickynote"
    display_name: "stickynote"
}
```
### 5. TFRecord 파일 생성
앞서 생성한 csv파일을 기반으로 TFRecord 파일을 생성해주어야한다.  
TFRecord : 학습에 사용할 데이터셋의 바이너리 포맷  
  
위의 label map과 같이 generate_tfrecord.py에서 class_text_to_int()의 내용을 수정한다.
```python
def class_text_to_int(row_label):
    if row_label == 'stickynote':
        return 1
    else:
        None
```

```bash
# test용 데이터셋 TFRecord 생성
python generate_tfrecord.py --csv_input=images\test_labels.csv --image_dir=images\test --output_path=test.record

# train용 데이터셋 TFRecord 생성
python generate_tfrecord.py --csv_input=images\train_labels.csv --image_dir=images\train --output_path=train.record 
```


### 6. pre-trained 모델 다운로드 & pipeline.config 설정
[model zoo](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/tf2_detection_zoo.md)에서 평균 탐색시간과 평균 객체 인식률을 비교해 적절한 모델을 다운로드  
모델파일의 압축을 풀면 아래와 같은 구조가 있음
```bash
├─ssd_mobilenet_v2_fpnlite_640x640_coco17_tpu-8
│  │  pipeline.config
│  │
│  ├─checkpoint
│  │      checkpoint
│  │      ckpt-0.data-00000-of-00001
│  │      ckpt-0.index
│  │
│  └─saved_model
│      │  saved_model.pb
│      │
│      └─variables
│              variables.data-00000-of-00001
│              variables.index
```
해당 구조를 유지한 채로, pipeline.config의 내용을 수정  
```bash
# 주요 수정 구간
num_classes: [label map에서 작성한 인식할 객체의 종류 갯수]
...
batch_size: [연산 한 번에 들어가는 데이터의 크기, 적당히 4정도, 너무 크면 OOM발생]
...
fine_tune_checkpoint: [학습을 시작할 checkpoint의 경로, pre-trained 모델의 checkpoint/ckpt-0]
num_steps: [학습 step수, 보통 20000]
fine_tune_checkpoint_type: "detection" [객체를 detection할 것이므로 이렇게 수정]
...
train_input_reader {
  label_map_path: [label map.pbtxt의 경로]
  tf_record_input_reader {
    input_path: [train용 tfrecord의 경로]
  }
}
...
eval_input_reader {
  label_map_path: [label map.pbtxt의 경로]
  shuffle: false
  num_epochs: 1
  tf_record_input_reader {
    input_path: [test용 tfrecord의 경로]
  }
}
```
### 7. 이미지 학습
위의 세팅이 완료되면 본격적으로 학습을 시작,
```bash
python model_main_tf2.py —-pipeline_config_path=[pipeline.config의 경로] -—model_dir=[학습 결과물들이 저장될 경로] —-logtostderr
```

### 8. 학습 과정 모니터링
학습 과정을 모니터링 할 수 있는 툴로 tensorboard가 있다.  
API 설치시 같이 딸려오므로 학습 실행시켜두고 모니터링 커맨드 실행
```bash
tensorboard --logdir=[학습 결과물들이 저장될 경로]
```

## 학습 이후 추론(Detecting)
- 모델 추출 : 학습을 완료하면 checkpoint가 생성되는데, 이를 model로 export 해줘야 한다.  
```bash
python exporter_main_v2.py --input_type=image_tensor --trained_checkpoint_dir=[학습 결과물들이 저장될 경로]--output_directory=[결과 model이 저장될 경로] --pipeline_config_path=[pipeline.config의 경로]
```

- 실제 추론(Detecting) : - 이렇게 추출된 model을 바탕으로 실제 추론(detecting)을 한다.  
예시 코드는 colab_tutorials의 object_detection_tutorial.ipynb에 있음  
Imports 부분 부터 쭉 실행  
  
PATH_TO_LABELS를 라벨맵의 경로로 수정, PATH_TO_TEST_IMAGES_DIR를 실제 detection에 사용할 이미지 경로로 수정  
  
detection_model의 경로를 학습하고 모델로 export한 경로(exported_model) 수정  
  
[[detection 코드 작성 예정]]