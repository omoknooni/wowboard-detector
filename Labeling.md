# 데이터 라벨링

## Repository
- [LabelImg](https://github.com/heartexlabs/labelImg)

## 환경
- Anaconda 22.9.0(Python 3.9.16)
- Windows 10 Pro

## 이미지 준비
학습에 사용할 이미지를 준비하는 과정으로, 와우보드에 포스트잇을 배치하고 사진을 촬영한다.  

학습용 이미지 촬영 시 다음 사항을 준수해야한다.
- **와우보드 전체가 모두 나오도록 사진을 촬영한다**  
- **촬영되는 사진의 비율은 1:1로 설정한다**  
- **보드 밖의 포스트잇은 나오지 않도록 상황을 설정한다**     

|라벨링하기에 부적절한 사례|이미지 예시|
|--|--|
|와우보드가 모두 나오지 않음|<img src="./mdImg/IMG_1486.jpg" width="500">|
|촬영된 이미지의 비율이 1:1이 아님|<img src="./mdImg/20230404_201402.jpg" width="500">|
|보드 밖의 포스트잇이 촬영됨|<img src="./mdImg/20230404_193100(1).jpg" width="500">|

이미지를 촬영 후, **사이즈를 조절해 주어야한다**  
기본적으로 폰 카메라로 촬영하는 경우 사이즈가 약 3000x3000으로 사이즈가 크게 찍히는데, 이런 경우 학습과정에서 이미지를 일부 구간만 인식하게 되어 학습이 재대로 되지 못한다.
따라서, 첨부된 image_resizer.py를 통해 1024x1024 사이즈로 자르는 작업이 필요하다.  


학습할 이미지들을 한 폴더에 모두 넣는다, 이미지 파일명에는 가급적 특수문자 넣는것을 피한다.  
되도록 파일명을 20230327_181452.jpg와 같이 직관적으로 한다. (특수문자 삽입만 피하자)

## 설치
> !! labelImg에 python 버전 이슈있으므로 3.9로 설치한다. !!  
[python 버전 이슈](https://github.com/heartexlabs/labelImg/issues/811)
```bash
### Conda를 사용하는 경우 ###
# 가상환경 생성(텐서플로 가상환경에서 설치할 경우 디펜던시 깨질 수 있음)
# labelImg에 python 버전 이슈 있음, 3.9로 설치
conda create -n labelimg python=3.9

# 가상환경 진입
conda activate labelimg

# labelImg 설치
pip install labelImg

# labelImg 실행
labelImg
```

```bash
### python 기본 가상환경을 사용하는 경우 ###
# 가상환경 생성
python -m venv labelimg

# 가상환경 진입 (윈도우)
./labelimg/Script/activate

# 가상환경 진입 (Mac/linux)
source ./labelimg/Script/activate

# labelImg 설치
pip install labelImg

# labelImg 실행
labelImg
```

## 라벨링
labelImg를 정상적으로 실행 후, 다음과 같은 화면, 'Open Dir'로 이미지 폴더 선택  
![img1](./mdImg/20230327_191712.png)
이미지 디렉토리 오픈, 이미지 로딩 및 목록 불러오는 것을 확인  
'Create RectBox' 클릭 혹은 단축키 'w'로 이미지 캡쳐 모드  

라벨링 모드는 PascalVOC로 설정한다. (기본값이 PascalVOC임)  
학습할 부분인 포스트잇을 캡쳐 후, 다음 팝업창에서 'stickynote' 입력  
와우보드도 마찬가지로 캡쳐 후, 다음 팝업창에서 'wowboard' 입력  

> **라벨링 시 라벨 이름 고정!**
> 1. stickynote : 포스트잇
> 2. wowboard : 와우보드

![img2](./mdImg/20230327_192304.png)

이후 해당 이미지 내의 모든 학습할 부분 캡쳐 후 'Save'로 xml파일 저장
![img3](./mdImg/20230327_193118.png)
![img4](./mdImg/20230327_193209.png)

## 데이터 업로드
라벨링 완료된 데이터는 이미지 파일과 xml 파일 모두를 [팀 드라이브](https://kyonggiackr-my.sharepoint.com/:f:/g/personal/jamsilkes_kyonggi_ac_kr/En2IW2YjSPpIn_DMN7gLc1IBBM_A2cmBvMMqOg4x1qVQfQ?e=8m6rwQ) 내 알맞은 폴더에 업로드하여 학습에 사용될 수 있도록 한다. 

드라이브 접속 시 학교 계정 로그인 필수.
