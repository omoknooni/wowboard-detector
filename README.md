# wowboard-detector

## 개발환경
- Anaconda 22.9.0(Python 3.9.16)
- Tensorflow 2.10
- Protoc 22.0
- Visual Studio 2022


## 설치
[Tensorflow Object Detection API](https://github.com/tensorflow/models/tree/master/research/object_detection)를 git clone해 설치

## 데이터 준비 및 학습
### 1. 데이터 수집
와우보드 위에 직접 포스트잇을 붙여서 촬영한 이미지와 단순히 포스트잇을 중심으로 한 이미지를 수집
### 2. 데이터 라벨링
학습에 사용하기 위해 수집한 이미지 데이터를 라벨링하는 작업이 필요하다.  
LabelImg라는 오픈소스 툴을 이용해 작업을 진행한다.

```bash
# install
pip install labelImg

# 실행
labelImg
```

이미지데이터를 불러오고 오브젝트 영역(Bounding Box)을 지정, 학습데이터는 xml파일로 저장됨
### 3. 단일 CSV파일 생성
각 이미지 별로 xml파일이 생성되었는데, 이를 하나의 csv파일로 묶어주어야 한다.
### 4. TFRecord 파일 생성
앞서 생성한 csv파일을 기반으로 TFRecord 파일을 생성해주어야한다.
### 5. Label Map 생성
인식할 객체의 정보를 담은 파일로 위의 데이터셋에서 라벨링했던 내용을 포함한다.
```
item {
    id: 1
    name: "stickynote"
    display_name: "stickynote"
}
```
### 6. 학습