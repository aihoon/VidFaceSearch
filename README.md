
# Face Analysis Function

## description
* Face 관련한 다양한 기능을 수행하는 function
  * Face detection
  * Face recognition
  * Face attribute(gender,race, age) estimation
  * Face mask detection

## Prerequisites
* 사용하려는 알고리즘을 subfolder에 clone 해야 한다.
  * git clone https://github.com/smartx-algorithm/minds_retinaface.git
  * git clone https://github.com/smartx-algorithm/minds_fairface.git
  * git clone https://github.com/smartx-algorithm/minds_maskcnn.git
 
------------------







* 제공하는 algorithm
  * facenet_pytorch at CPU, cuda, and cuda:*


* 3 개의 동작 모드를 지원한다.
  * image path processing
  * video file processing
  * image processing server

## Prerequisites

* facenet_pytorch 에서 embedding 과 classification 기능을 동시에 수행하기 위해   
  inception_resnet_v1.py 를 수정해야 한다.
  * InceptionResnetV1 class 에서 self.embedding 변수 추가
  * InceptionResnetV1.forward 에서 "*x = self.last_bn(x)*" 뒤에   
    "*self.embedding = F.normalize(x, p=2, dim=1)*" 을 추가

## Module Server Interface Protocol

### "**Health Check**" Protocol  
* Request   
  ```json
    {"cmd": "check"}
  ```
* Response
  * 정상일 경우   
    ```json
      {"state": "healthy"}
    ```
  * 비정상일 경우   
    ```json
      {"state": "Invalid"}
    ```

### "**Run**" Protocol  
* Request
```javascript
  {     
    "cmd": "run",   
    "request":
      {
        "mmap_fname": memory_map_filename,   
        "mmap_shape": numpy_array_shape,   
        "roi": roi_list
      }
  }
```
  * memory_map_filename 은 numpy memory map 의 파일이름이며 string 타입이다.   
  * numpy_array_shape 은 numpy array 의 shape 이며 tuple 타입이다.
  * roi 는 0 과 1 사이의 네개의 실수로 구성되며 list 타입이다.

* Response
  * 정상일 경우
  ```javascript
    {
      "state": "Done",
      "response":
      {
        "result": success",
        "face_info":
          {
            "face_box_arr": face_box_arr,
            "face_embedding_arr": face_embedding_arr, 
            "face_name_arr": face_name_arr,
            "face_err_arr": face_err_arr,
            "elapsed_time": elapsed_time
          },
        "proc_time": proc_time
      }
    }   
  ```   
    * face_box_arr 는 0 과 1 사이의 4 개의 실수로 이루어진 bounding box 의 array 이다.
    * face_embedding_arr 는 face embedding vector 로써 하나의 얼굴은 float type 의 512 개로 구성된다.
    * face_name_arr 는 검출한 face name 이름의 array 이다.
    * face_err_arr 는 검출한 face name 의 error 이다.
    * elapsed_time 은 face recognition 에 소요된 시간이다.   

  * 비정상일 경우
  ```javascript
    {
      "state": "Done",
      "response":
      {
        "result": "fail",
        "description": fail_description
      }
    }
    ```
    * fail_description 은 정상 동작에 실패한 이유가 기록된다.

## Module Test

### Operation Test

#### Image Path Processing    
* Image path 폴더에 있는 모든 이미지 파일을 처리한다.

#### Video File processing
* Video file 을 처리한다.

#### Image Processing Server
* FaceRecognition_client.py 와의 handshake 을 통해 image 를 처리한다.

### Parameter Test

#### "detect_height" parameter
* Face recognition 함수로 입력되는 이미지의 크기를 고정하는 변수이다.
* 매우 큰 이미지가 들어올 경우, 계산 시간을 줄이기 위해 적당한 이미지로 resize 한 이후 face recognition 을 수행한다.
* Face recognition 결과는 변경된 이미지에 대한 결과이므로, 이를 다시 원 이미지 크기에 맞춰 재조정되는지 확인해야 한다.
* *ini['FACE_RECOGNITION']['detect_height']* 값을 변화시켜 가면서 object detection 결과를 확인해야 한다.

#### "roi" parameter
* Face recognition 을 수행하는 영역을 정의하는 변수이다.
* 이를 조정해 가면서 face recognition 이 그 영역에서만 동작하는지 확인해야 한다.
* ini['FACE_RECOGNITION']['roi'] 값을 변화시켜 가면서 face recognition 결과를 확인해야 한다.

#### "device" parameter
* Face recognition 을 수행하는 device 를 정의하는 변수이다.
* cpu, cuda, cuda:0, cuda:1 등을 지정할 수 있다.
* cpu 보다 cuda 를 사용했을 경우 몇배가 빨리지는 지를 확인하여 cuda device 가 동작하는지 확인해야 한다.

## Module Test Summary
| category | Task | Result | Remark |
| -------- | -----| ----------- | ------ |
| Operation test | Image path processing   | Y | hoon @ 200325|
| Operation test | Video path processing   | Y | hoon @ 200325|
| Operation test | Image processing server | Y | hoon @ 200325|
| Parameter test | detection height        | Y | hoon @ 200325|
| Parameter test | roi                     | Y | hoon @ 200325|
| Parameter test | device                  | Y | hoon @ 200325|

